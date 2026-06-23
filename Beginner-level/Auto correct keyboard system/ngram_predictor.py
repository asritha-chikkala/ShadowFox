import nltk
from collections import defaultdict, Counter
import time
import pickle
import os
import re
import math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(SCRIPT_DIR, "ngram_model_v4.pkl")

_SKIP_TOKENS = frozenset([
    ".", ",", ";", ":", "?", "!", "<end>", "<s>", "</s>",
    "``", "''", "--", "...", "'s",
])


class NextWordPredictor:
    MODEL_VERSION = 4

    def __init__(self):
        self.bigram_model = defaultdict(Counter)
        self.trigram_model = defaultdict(Counter)
        self.quadgram_model = defaultdict(Counter)
        self.fivegram_model = defaultdict(Counter)
        self.unigram_counts = Counter()
        self.vocab_size = 0
        self.total_words = 0
        self.is_trained = False

        if self._load_model():
            print(f"Loaded pre-trained n-gram model from {MODEL_FILE}")
        else:
            print("Training n-gram model (first run may take 1-2 minutes)...")
            self._download_resources()
            self._train_model()
            self._save_model()
            print(f"Training complete. Model saved to {MODEL_FILE}")

    def _load_model(self) -> bool:
        try:
            if os.path.exists(MODEL_FILE):
                with open(MODEL_FILE, "rb") as f:
                    data = pickle.load(f)
                if data.get("version") != self.MODEL_VERSION:
                    print("Model version mismatch - retraining.")
                    return False
                self.bigram_model = data["bigram"]
                self.trigram_model = data["trigram"]
                self.quadgram_model = data["quadgram"]
                self.fivegram_model = data.get("fivegram", defaultdict(Counter))
                self.unigram_counts = data["unigram"]
                self.vocab_size = data["vocab_size"]
                self.total_words = data.get("total_words", sum(self.unigram_counts.values()))
                self.is_trained = True
                return True
        except Exception as e:
            print(f"Warning: could not load model ({e}). Retraining.")
        return False

    def _save_model(self):
        try:
            with open(MODEL_FILE, "wb") as f:
                pickle.dump({
                    "version": self.MODEL_VERSION,
                    "bigram": self.bigram_model,
                    "trigram": self.trigram_model,
                    "quadgram": self.quadgram_model,
                    "fivegram": self.fivegram_model,
                    "unigram": self.unigram_counts,
                    "vocab_size": self.vocab_size,
                    "total_words": self.total_words,
                }, f)
        except Exception as e:
            print(f"Warning: could not save model ({e}).")

    def _download_resources(self):
        resources = {
            "tokenizers/punkt": "punkt",
            "tokenizers/punkt_tab": "punkt_tab",
            "corpora/reuters": "reuters",
            "corpora/brown": "brown",
            "corpora/gutenberg": "gutenberg",
            "corpora/webtext": "webtext",
            "corpora/inaugural": "inaugural",
        }
        for path, name in resources.items():
            try:
                nltk.data.find(path)
            except LookupError:
                print(f"  Downloading {name}...")
                nltk.download(name, quiet=True)
                time.sleep(0.5)

    @staticmethod
    def _clean_tokens(raw_tokens):
        out = []
        for t in raw_tokens:
            t = t.lower()
            if re.fullmatch(r"[^a-z0-9']+", t):
                continue
            if re.fullmatch(r"\d[\d,\.]*", t):
                t = "<num>"
            out.append(t)
        return out

    def _add_to_models(self, words: list):
        n = len(words)
        for i in range(n):
            self.unigram_counts[words[i]] += 1
            self.total_words += 1
        for i in range(n - 1):
            self.bigram_model[words[i]][words[i + 1]] += 1
        for i in range(n - 2):
            self.trigram_model[(words[i], words[i + 1])][words[i + 2]] += 1
        for i in range(n - 3):
            self.quadgram_model[(words[i], words[i + 1], words[i + 2])][words[i + 3]] += 1
        for i in range(n - 4):
            self.fivegram_model[(words[i], words[i + 1], words[i + 2], words[i + 3])][words[i + 4]] += 1

    def _train_model(self):
        from nltk.corpus import reuters, brown, gutenberg, webtext, inaugural

        corpus_iters = [
            ("Reuters", (reuters.words(fid) for fid in reuters.fileids())),
            ("Brown", brown.sents()),
            ("Gutenberg", (gutenberg.words(fid) for fid in gutenberg.fileids())),
            ("Web/Blogs", webtext.sents()),
            ("Inaugural", inaugural.sents()),
        ]

        total = 0
        for corpus_name, iterator in corpus_iters:
            try:
                for item in iterator:
                    words = self._clean_tokens(item)
                    if len(words) > 5:
                        self._add_to_models(words)
                        total += 1
                        if total % 5000 == 0:
                            print(f"  {total:,} chunks processed...")
            except Exception as e:
                print(f"  Skipping {corpus_name}: {e}")

        self.unigram_counts = Counter({
            w: c for w, c in self.unigram_counts.items() if c > 1
        })
        self.vocab_size = len(self.unigram_counts)
        self.is_trained = True

        print(f"\n  Done. Chunks={total:,} | Vocab={self.vocab_size:,}")
        print(f"  Bigrams={len(self.bigram_model):,} "
              f"Trigrams={len(self.trigram_model):,} "
              f"Quadgrams={len(self.quadgram_model):,} "
              f"Fivegrams={len(self.fivegram_model):,}")

    @staticmethod
    def _tokenize_input(text: str) -> list:
        tokens = text.lower().split()
        cleaned = []
        for t in tokens:
            t = re.sub(r"[^a-z0-9'<>]", "", t)
            if t:
                cleaned.append(t)
        return cleaned

    def _from_counter_with_smoothing(self, counter: Counter, top_n: int, total: int, alpha: float = 0.1) -> list:
        """
        Get top predictions with Add-k (Laplace) smoothing.
        alpha = smoothing parameter (0.1 works well for this task)
        """
        vocab_size = self.vocab_size or 1
        
        # Get raw counts
        raw_predictions = counter.most_common(top_n * 5)
        
        # Apply Add-k smoothing: P(w|context) = (count(w) + alpha) / (total + alpha * vocab_size)
        smoothed_predictions = []
        for word, count in raw_predictions:
            if word in _SKIP_TOKENS:
                continue
            if word not in self.unigram_counts:
                continue
            
            # Smoothed probability with Add-k
            smoothed_prob = (count + alpha) / (total + alpha * vocab_size)
            prob_percent = smoothed_prob * 100
            smoothed_predictions.append((word, round(prob_percent, 1)))
            if len(smoothed_predictions) >= top_n:
                break
        
        return smoothed_predictions

    def _unigram_fallback(self, top_n: int) -> list:
        common = [
            w for w, _ in self.unigram_counts.most_common(top_n * 4)
            if w not in _SKIP_TOKENS and not w.startswith("<")
        ]
        total = sum(self.unigram_counts.values())
        return [
            (w, round(self.unigram_counts[w] / total * 100, 2))
            for w in common[:top_n]
        ]

    def predict_next(self, text: str, top_n: int = 5) -> list:
        if not self.is_trained or not text or not text.strip():
            return []

        words = self._tokenize_input(text)
        if not words:
            return []

        # Try 5-gram first (more context = better accuracy)
        if len(words) >= 4:
            ctx = (words[-4], words[-3], words[-2], words[-1])
            if ctx in self.fivegram_model:
                total = sum(self.fivegram_model[ctx].values())
                if total > 0:
                    result = self._from_counter_with_smoothing(
                        self.fivegram_model[ctx], top_n, total, alpha=0.1
                    )
                    if result:
                        return result

        # Fallback to 4-gram
        if len(words) >= 3:
            ctx = (words[-3], words[-2], words[-1])
            if ctx in self.quadgram_model:
                total = sum(self.quadgram_model[ctx].values())
                if total > 0:
                    result = self._from_counter_with_smoothing(
                        self.quadgram_model[ctx], top_n, total, alpha=0.15
                    )
                    if result:
                        return result

        # Fallback to 3-gram
        if len(words) >= 2:
            ctx = (words[-2], words[-1])
            if ctx in self.trigram_model:
                total = sum(self.trigram_model[ctx].values())
                if total > 0:
                    result = self._from_counter_with_smoothing(
                        self.trigram_model[ctx], top_n, total, alpha=0.2
                    )
                    if result:
                        return result

        # Fallback to 2-gram
        last = words[-1]
        if last in self.bigram_model:
            total = sum(self.bigram_model[last].values())
            if total > 0:
                result = self._from_counter_with_smoothing(
                    self.bigram_model[last], top_n, total, alpha=0.3
                )
                if result:
                    return result

        return self._unigram_fallback(top_n)

    def evaluate_accuracy(self, test_sentences):
        total = 0
        correct_top1 = 0
        correct_top5 = 0

        for sentence in test_sentences:
            words = self._tokenize_input(sentence)

            if len(words) < 4:
                continue

            for i in range(3, len(words)):
                context = " ".join(words[:i])
                actual = words[i]

                predictions = self.predict_next(context, top_n=5)

                if not predictions:
                    continue

                predicted_words = [word for word, _ in predictions]

                total += 1

                if predicted_words and predicted_words[0] == actual:
                    correct_top1 += 1

                if actual in predicted_words:
                    correct_top5 += 1

        if total == 0:
            return 0.0, 0.0

        top1 = (correct_top1 / total) * 100
        top5 = (correct_top5 / total) * 100

        return round(top1, 2), round(top5, 2)

    def benchmark_latency(self):
        samples = [
            "i would like",
            "machine learning is",
            "the weather today",
            "thank you for",
            "artificial intelligence can",
            "this project uses",
            "next word prediction"
        ]

        runs = 100

        start = time.perf_counter()

        for _ in range(runs):
            for text in samples:
                self.predict_next(text)

        end = time.perf_counter()

        total_predictions = runs * len(samples)

        latency_ms = ((end - start) / total_predictions) * 1000

        return round(latency_ms, 3)

    def get_statistics(self):
        return {
            "Vocabulary Size": self.vocab_size,
            "Bigrams": len(self.bigram_model),
            "Trigrams": len(self.trigram_model),
            "Quadgrams": len(self.quadgram_model),
            "Fivegrams": len(self.fivegram_model)
        }