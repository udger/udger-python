
class WordDetector(object):

    _wdict = {}

    def add_word(self, wid, word):
        prefix = word[:3]
        if prefix not in self._wdict:
            self._wdict[prefix] = [(wid,word),]
        else:
            self._wdict[prefix].append((wid,word),)

    def find_words(self, text):
        found_words = set()
        found_words.add(0)
        s = text.lower()
        for x in range(0, len(s) - 2):
            word_infos = self._wdict.get(s[x:x+3], ())
            found_words.update(wi[0] for wi in word_infos if s.startswith(wi[1], x))
        return found_words