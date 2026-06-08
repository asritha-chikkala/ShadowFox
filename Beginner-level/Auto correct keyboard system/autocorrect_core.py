import re
from spellchecker import SpellChecker

COMMON_WORD_BOOST = {
    "their", "there", "they're", "your", "you're", "its", "it's",
    "then", "than", "affect", "effect", "accept", "except",
    "lose", "loose", "principal", "principle", "complement", "compliment",
    "discrete", "discreet", "ensure", "insure", "assure",
    "further", "farther", "lay", "lie", "raise", "rise",
    "good", "well", "bad", "badly", "less", "fewer",
}

COMMON_TYPOS = {
    "teh": "the", "adn": "and", "waht": "what", "taht": "that",
    "hte": "the", "fo": "of", "ot": "to", "ti": "it",
    "recieve": "receive", "beleive": "believe", "occured": "occurred",
    "seperate": "separate", "definately": "definitely", "neccessary": "necessary",
    "accomodate": "accommodate", "occassion": "occasion", "wierd": "weird",
    "calender": "calendar", "cemetary": "cemetery", "concious": "conscious",
    "embarass": "embarrass", "existance": "existence", "foriegn": "foreign",
    "goverment": "government", "grammer": "grammar", "harrass": "harass",
    "independant": "independent", "knowlege": "knowledge", "liason": "liaison",
    "medival": "medieval", "millenium": "millennium", "mispell": "misspell",
    "noticable": "noticeable", "occurance": "occurrence", "perseverence": "perseverance",
    "posession": "possession", "priviledge": "privilege", "publically": "publicly",
    "restaraunt": "restaurant", "rythm": "rhythm", "speach": "speech",
    "succesful": "successful", "suprise": "surprise", "tommorrow": "tomorrow",
    "tounge": "tongue", "truely": "truly", "untill": "until",
    "vaccum": "vacuum", "visable": "visible", "writting": "writing",
    "aboslutely": "absolutely", "basicaly": "basically", "belive": "believe",
    "buisness": "business", "carrer": "career", "commitee": "committee",
    "consistant": "consistent", "differance": "difference", "excercise": "exercise",
    "friendaly": "friendly", "guarentee": "guarantee", "happend": "happened",
    "imediately": "immediately", "interupt": "interrupt", "lightening": "lightning",
    "managment": "management", "missle": "missile", "nineth": "ninth",
    "persistance": "persistence", "questionaire": "questionnaire", "relevent": "relevant",
    "reciept": "receipt", "referance": "reference", "sieze": "seize",
    "shouldnt": "shouldn't", "wouldnt": "wouldn't", "couldnt": "couldn't",
    "doesnt": "doesn't", "didnt": "didn't", "wasnt": "wasn't",
    "isnt": "isn't", "arent": "aren't", "havent": "haven't",
    "wont": "won't", "cant": "can't", "dont": "don't",
}


class AutocorrectEngine:
    def __init__(self):
        self.spell = SpellChecker()
        self.spell.word_frequency.load_words(list(COMMON_WORD_BOOST))

    def _split_word(self, token):
        match = re.match(r"^(\W*)(\w[\w'-]*)(\W*)$", token)
        if match:
            return match.group(1), match.group(2), match.group(3)
        return "", token, ""

    def _preserve_case(self, original: str, correction: str) -> str:
        if not original or not correction:
            return correction
        if original.isupper():
            return correction.upper()
        if original.istitle() or original[0].isupper():
            return correction.capitalize()
        return correction.lower()

    def _best_correction(self, word_lower: str):
        if word_lower in COMMON_TYPOS:
            return COMMON_TYPOS[word_lower]
        return self.spell.correction(word_lower)

    def _ranked_suggestions(self, word_lower: str, top_n: int = 6) -> list:
        suggestions = []

        if word_lower in COMMON_TYPOS:
            suggestions.append(COMMON_TYPOS[word_lower])

        candidates = self.spell.candidates(word_lower) or set()
        ranked = sorted(
            candidates,
            key=lambda w: self.spell.word_frequency[w],
            reverse=True,
        )

        for w in ranked:
            if w not in suggestions:
                suggestions.append(w)
            if len(suggestions) >= top_n:
                break

        best = self._best_correction(word_lower)
        if best and best in suggestions and suggestions[0] != best:
            suggestions.remove(best)
            suggestions.insert(0, best)
        elif best and best not in suggestions:
            suggestions.insert(0, best)

        return suggestions[:top_n]

    def is_known(self, word_lower: str) -> bool:
        if len(word_lower) == 1 and word_lower in ("a", "i"):
            return True
        return word_lower in self.spell

    def correct_sentence(self, sentence: str):
        if not sentence or not sentence.strip():
            return "", [], {}

        words = sentence.split()
        corrected_words = []
        corrections_made = []
        suggestions_dict = {}

        for token in words:
            prefix, core, suffix = self._split_word(token)

            if not core:
                corrected_words.append(token)
                continue

            core_lower = core.lower()

            if self.is_known(core_lower):
                corrected_words.append(token)
                continue

            suggestions = self._ranked_suggestions(core_lower, top_n=6)
            suggestions_dict[core] = suggestions

            best = self._best_correction(core_lower)
            if best and best != core_lower:
                best_cased = self._preserve_case(core, best)
                corrected_token = prefix + best_cased + suffix
                corrected_words.append(corrected_token)
                if corrected_token != token:
                    corrections_made.append(f"{token} → {corrected_token}")
            else:
                corrected_words.append(token)

        return " ".join(corrected_words), corrections_made, suggestions_dict

    def check_word(self, word: str):
        prefix, core, suffix = self._split_word(word)

        if not core:
            return True, None, []

        core_lower = core.lower()

        if self.is_known(core_lower):
            return True, None, []

        suggestions = self._ranked_suggestions(core_lower)
        best = self._best_correction(core_lower)

        if best:
            best_cased = self._preserve_case(core, best)
            corrected_word = prefix + best_cased + suffix
            return False, corrected_word, suggestions

        return False, None, suggestions

    def get_suggestions(self, word: str, top_n: int = 6) -> list:
        _, core, _ = self._split_word(word)
        return self._ranked_suggestions(core.lower(), top_n=top_n)