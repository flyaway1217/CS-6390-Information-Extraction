# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-02-26 15:36:16
# Last modified: 2017-03-01 16:45:19

"""
Implementation of DIRT algorithm
"""


class Triple:
    def __init__(self, slotX, path, slotY):
        """Construct a new Triple.

        Args:
            slotX: str - The left of the path.
            path: str - Sequence between two NPs.
            slotY: str - The right of the path.
        """
        self._slotX = slotX.strip()
        self._path = path.strip()
        self._slotY = slotY.strip()

        # x = ' '.join(self._slotX)
        # y = ' '.join(self._slotY)
        # z = ' '.join(self._path)
        # self._hash = hash(x+y+z)
        self._hash = hash(slotX+path+slotY)

    ########################################################
    # Property
    ########################################################
    @property
    def slotX(self):
        return self._slotX

    @property
    def slotY(self):
        return self._slotY

    @property
    def path(self):
        return self._path

    ########################################################
    # Magic methods
    ########################################################
    def __eq__(self, other):
        return self._hash == other._hash

    def __hash__(self):
        return self._hash

    def __repr__(self):
        s = [self.slotX, self.path, self.slotY]
        return '||'.join(s)


class IOManager:
    def __init__(self):
        pass

    def read_sentences(self, path):
        """Read the sentences from the given path.

        Yield:
            words: list(str) - A list of words
            poss: list(str) - A list of pos tags.
        """
        with open(path, encoding='utf8') as f:
            words = []
            poss = []
            for line in f:
                s = line.strip().split(':')
                pos = s[0].strip()
                word = s[1].strip()
                if pos == 'WORD' and word == '<EOS':
                    yield words, poss
                    words = []
                    poss = []
                else:
                    words.append(word.strip().lower())
                    poss.append(pos.strip().lower())

    def read_phrases(self, path):
        """Read the test phrases.
        Each line contains one phrase.

        Args:
            path:str - The path of illegal phrase file.
        """
        reval = []
        with open(path, encoding='utf8') as f:
            for line in f:
                phrase = line.strip().lower()
                reval.append(phrase)
        return reval


class Extractor:
    """Extractor for triples.
    """
    def __init__(self, illegal_path):
        self._illegal_phrases = self._read_phrase(illegal_path)

    def extract(self, words, poss):
        raw_triples = self._extract(words, poss)
        return self._tunning(raw_triples)

    def _extract(self, words, poss):
        """Extract the raw triples from the given sentence.

        Args:
            words: list(str) - A list of phrases
            poss: list(str) - A list of pos tags.

        Returns:
            list(list(str))
        """
        assert len(words) == len(poss)
        reval = []
        try:
            i = poss.index('np')
        except ValueError:
            return reval

        while True:
            try:
                j = poss.index('np', i+1)
            except ValueError:
                break
            if j > i+1:
                reval.append(words[i:j+1])
            i = j
        return reval

    def _read_phrase(self, path):
        """Read the illegal phrases.
        Each line contains one phrase.

        Args:
            path:str - The path of illegal phrase file.
        """
        reval = set()
        with open(path, encoding='utf8') as f:
            for line in f:
                phrase = line.strip().lower()
                reval.add(phrase)
        return reval

    def _tunning(self, raw_triples):
        """Fine tunning the raw triples.

        1. Select the head noun to fill the slots.
        2. Remove the illegal paths

        Args:
            raw_triples: list(list(word)) - A list of raw triples.

        Returns:
            list(Triple)
        """
        reval = []
        for raw in raw_triples:
            # Filter the illegal triples
            if len(raw) == 3:
                if raw[1].strip() in self._illegal_phrases:
                    continue

            # Use the right most as the head word.
            slotX = raw[0].split()[-1]
            slotY = raw[-1].split()[-1]
            path = ' '.join(raw[1:-1])
            triple = Triple(slotX, path, slotY)
            reval.append(triple)
        return reval
