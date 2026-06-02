import re
from spellchecker import SpellChecker

class AutocorrectEngine:
    def __init__(self):
        self.spell = SpellChecker()
    
    def _extract_word_with_punctuation(self, word):
        match = re.match(r"^(\W*)(\w+)(\W*)$", word)
        if match:
            prefix, clean_word, suffix = match.groups()
            return prefix, clean_word, suffix
        return "", word, ""
    
    def _preserve_capitalization(self, original, correction):
        if not original or not correction:
            return correction
        if original.isupper():
            return correction.upper()
        elif original.istitle():
            return correction.capitalize()
        return correction.lower()
    
    def correct_sentence(self, sentence):
        if not sentence or not sentence.strip():
            return "", [], {}
        
        words = sentence.split()
        corrected_words = []
        corrections_made = []
        suggestions_dict = {}
        
        for word in words:
            prefix, clean_word, suffix = self._extract_word_with_punctuation(word)
            
            if not clean_word:
                corrected_words.append(word)
                continue
            
            clean_lower = clean_word.lower()
            
            if clean_lower in self.spell:
                corrected_words.append(word)
            else:
                correction = self.spell.correction(clean_lower)
                suggestions = self.get_suggestions(clean_lower, correction=correction, top_n=5)
                suggestions_dict[clean_word] = suggestions
                
                if correction:
                    correction = self._preserve_capitalization(clean_word, correction)
                    corrected_word = prefix + correction + suffix
                    corrected_words.append(corrected_word)
                    corrections_made.append(f"{word} → {corrected_word}")
                else:
                    corrected_words.append(word)
        
        corrected_sentence = ' '.join(corrected_words)
        return corrected_sentence, corrections_made, suggestions_dict
    
    def check_word(self, word):
        prefix, clean_word, suffix = self._extract_word_with_punctuation(word)
        
        if not clean_word:
            return True, None, []
        
        clean_lower = clean_word.lower()
        
        if clean_lower in self.spell:
            return True, None, []
        else:
            correction = self.spell.correction(clean_lower)
            suggestions = self.get_suggestions(clean_lower, correction=correction)
            
            if correction:
                correction = self._preserve_capitalization(clean_word, correction)
                corrected_word = prefix + correction + suffix
                return False, corrected_word, suggestions
            else:
                return False, None, suggestions
    
    def get_suggestions(self, word, correction=None, top_n=5):
        clean_word = word.lower().strip(".,!?;:\"'()")
        word_len = len(clean_word)
        
        suggestions = self.spell.candidates(clean_word)
        
        if suggestions:
            suggestions = list(suggestions)
            
            # Filter by length: word_len-1, word_len, word_len+1
            filtered_suggestions = [
                s for s in suggestions 
                if len(s) in [word_len - 1, word_len, word_len + 1]
            ]
            
            # If filtered results are too few, include all suggestions
            if len(filtered_suggestions) < top_n:
                filtered_suggestions = suggestions
            
            if correction is None:
                correction = self.spell.correction(clean_word)
            
            if correction and correction != clean_word and correction in filtered_suggestions:
                filtered_suggestions.remove(correction)
                filtered_suggestions.insert(0, correction)
            elif correction and correction != clean_word:
                filtered_suggestions.insert(0, correction)
            
            # Remove duplicates and limit to top_n
            unique_suggestions = []
            for s in filtered_suggestions:
                if s not in unique_suggestions:
                    unique_suggestions.append(s)
            
            return unique_suggestions[:top_n]
        
        return []