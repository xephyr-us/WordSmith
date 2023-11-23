from itertools import product
from random import choice


class Etymologist:

    INV_TERM_TYPE_MSG = "Invalid term type {} passed to {}"
    INV_TERM_MSG = "Invalid term {} passed to {}"

    def __init__(self):
        self._definitions = {}
        self._terms = {}

    def _check_term_type(self, term_type):
        if not self.is_term_type(term_type):
            msg = self.INV_TERM_TYPE_MSG.format(repr(term_type), repr(type(self).__name__))
            raise KeyError(msg) 

    def _check_term(self, term):
        if not self.is_term(term):
            msg = self.INV_TERM_MSG.format(repr(term), repr(type(self).__name__))
            raise KeyError(msg) 

    def add_terms(self, term_type, terms):
        self._terms[term_type] = tuple(terms.keys())
        self._definitions.update(terms)

    def remove_terms(self, term_type):
        self._check_term_type(term_type)
        for term in self._terms[term_type]:
            self._definitions.pop(term)
        self._terms.pop(term_type)
    
    def get_term_of_type(self, term_type):
        self._check_term_type(term_type)
        term = choice(self._terms[term_type])
        return term, self._definitions[term]

    def is_term_type(self, string):
        return string in self._terms

    def is_term(self, string):
        return string in self._definitions


class Neologist:

    PART_DELIM = "|"
    COND_DELIM = ","

    PHON_ASSIGN = ">"
    
    PLACE_TOKEN = "-"
    REPLACE_TOKEN = "~"

    TOKEN_VALUES = {
        "&": "aeiou",
        "$": "bcdfghjklmnpqrstvwxyz",
    }

    def __init__(self):
        self._word = None
        self._definition = None 
        self._cached_funcs = {}
        self._values = self.TOKEN_VALUES.copy()

    def _get_matching_phoneme(self, term):
        for part in term.split(self.PART_DELIM):
            cond, phoneme = self._split_part(part)
            is_backwards = phoneme.startswith(self.PLACE_TOKEN) or phoneme.startswith(self.REPLACE_TOKEN)
            result = self._get_cond_func(cond)(is_backwards)
            if result is not None:
                return phoneme, result
        msg = f"Invalid term passed to {repr(type(self).__name__)}, no default phoneme present"
        raise SyntaxError(msg)

    def _adjoin_phoneme(self, phoneme, index):
        if self.PLACE_TOKEN in phoneme:
            new = phoneme.replace(self.PLACE_TOKEN, self._word)
        elif self.REPLACE_TOKEN in phoneme:
            old = self._word[:index] if index < 0 else self._word[index:]
            new = phoneme.replace(self.REPLACE_TOKEN, old)
        else:
            new = phoneme
        self._word = new

    def _integrate_meaning(self, meaning):
        self._definition = meaning.replace("...", self._definition)

    def _parse_term(self, term):
        for part in term.split(self.PART_DELIM):
            yield self._split_part(part)

    def _split_part(self, part):
        if self.PHON_ASSIGN in part:
            cond, phoneme = part.split(self.PHON_ASSIGN)
        else:
            cond, phoneme = None, part
        return cond, phoneme
    
    def _get_cond_func(self, cond):
        if cond in self._cached_funcs:
            return self._cached_funcs[cond]
        if cond is None:
            func = lambda b: 0
        else:
            matches = self._get_cond_matches(cond)
            length = max(len(s) for s in cond.split(self.COND_DELIM))
            def func(backwards):
                decrement = -1 if backwards else 1
                index = -length if backwards else length 
                for _ in range(length):
                    portion = self._word[index:] if backwards else self._word[:index]
                    if portion in matches:
                        return index
                    index -= decrement
                return None
        self._cached_funcs[cond] = func
        return func

    def _get_cond_matches(self, cond):
        matches = set()
        for string in cond.split(self.COND_DELIM):
            current = [""]
            for c in string:
                value = self._values.setdefault(c, c)
                current = ["".join(t) for t in product(current, value)]
            matches |= set(current)
        return matches

    def push(self, term, meaning):
        if self._word is None or self._definition is None:
            self._word = term
            self._definition = meaning
        else:
            phoneme, placement = self._get_matching_phoneme(term)
            self._adjoin_phoneme(phoneme, placement)
            self._integrate_meaning(meaning)

    def pull(self):
        output = self._word, self._definition
        self._word = self._definition = None
        return output

