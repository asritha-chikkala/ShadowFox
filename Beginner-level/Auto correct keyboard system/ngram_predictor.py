import nltk
from collections import defaultdict, Counter
import time

class NextWordPredictor:
    def __init__(self):
        self.bigram_model = defaultdict(Counter)
        self.trigram_model = defaultdict(Counter)
        self.quadgram_model = defaultdict(Counter)
        self.is_trained = False
        self._download_resources()
        self._train_model()
    
    def _download_resources(self):
        resources = ['punkt', 'punkt_tab', 'reuters', 'brown']
        
        for resource in resources:
            try:
                if resource == 'punkt_tab':
                    nltk.data.find('tokenizers/punkt_tab')
                elif resource == 'punkt':
                    nltk.data.find('tokenizers/punkt')
                else:
                    nltk.data.find(f'corpora/{resource}')
            except LookupError:
                print(f"Downloading {resource}...")
                nltk.download(resource, quiet=True)
                time.sleep(1)
    
    def _train_model(self):
        print("Training ngram models on NLTK corpora...")
        
        try:
            from nltk.corpus import reuters, brown
            
            total_sentences = 0
            
            for fileid in reuters.fileids():
                words = reuters.words(fileid)
                if len(words) > 3:
                    words_lower = [w.lower() for w in words]
                    self._add_to_models(words_lower)
                    total_sentences += 1
                    if total_sentences % 2000 == 0:
                        print(f"  Processed {total_sentences} documents...")
            
            for sentence in brown.sents():
                if len(sentence) > 3:
                    words_lower = [w.lower() for w in sentence]
                    self._add_to_models(words_lower)
                    total_sentences += 1
                    if total_sentences % 5000 == 0:
                        print(f"  Processed {total_sentences} sentences...")
            
            self.is_trained = True
            print(f"Training complete! Processed {total_sentences} documents/sentences.")
            print(f"  Bigrams: {len(self.bigram_model)}")
            print(f"  Trigrams: {len(self.trigram_model)}")
            print(f"  Quadgrams: {len(self.quadgram_model)}")
            
        except Exception as e:
            print(f"Training error: {e}")
            self.is_trained = False
    
    def _add_to_models(self, words):
        for i in range(len(words)-1):
            self.bigram_model[words[i]][words[i+1]] += 1
        
        for i in range(len(words)-2):
            self.trigram_model[(words[i], words[i+1])][words[i+2]] += 1
        
        for i in range(len(words)-3):
            self.quadgram_model[(words[i], words[i+1], words[i+2])][words[i+3]] += 1
    
    def predict_next(self, text, top_n=5):
        if not self.is_trained:
            return []
        
        if not text or not text.strip():
            return []
        
        words = text.lower().split()
        
        if len(words) >= 3:
            last_three = (words[-3], words[-2], words[-1])
            if last_three in self.quadgram_model:
                predictions = self.quadgram_model[last_three]
                total = sum(predictions.values())
                result = []
                for word, count in predictions.most_common(top_n):
                    if word not in ['.', ',', ';', ':', '?', '!', '<END>']:
                        prob = (count / total) * 100
                        result.append((word, prob))
                if result:
                    return result
        
        if len(words) >= 2:
            last_two = (words[-2], words[-1])
            if last_two in self.trigram_model:
                predictions = self.trigram_model[last_two]
                total = sum(predictions.values())
                result = []
                for word, count in predictions.most_common(top_n):
                    if word not in ['.', ',', ';', ':', '?', '!', '<END>']:
                        prob = (count / total) * 100
                        result.append((word, prob))
                if result:
                    return result
        
        if len(words) >= 1:
            last_word = words[-1]
            if last_word in self.bigram_model:
                predictions = self.bigram_model[last_word]
                total = sum(predictions.values())
                result = []
                for word, count in predictions.most_common(top_n):
                    if word not in ['.', ',', ';', ':', '?', '!', '<END>']:
                        prob = (count / total) * 100
                        result.append((word, prob))
                if result:
                    return result
        
        return []