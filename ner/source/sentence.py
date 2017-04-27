# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-03-02 14:03:11
# Last modified: 2017-04-13 12:06:08

"""
Sentence structure for the NER project.
"""

import collections


POSITIONS = ['curr-', 'prev-', 'next-', 'prev2-', 'next2-']
WORDS = ['PHI', 'OMEGA', 'UNKWORD']
POS = ['PHIPOS', 'OMEGAPOS', 'UNKPOS']
OTHERS = ['$init-caps$', '$all-caps$', '$contains-dig$',
          '$all-dig$', '$punc-mark$', '$contains-dots$',
          '$contains-hypen$', '$single-char$']
LABELS = {
        'O': 0,
        'B-PER': 1,
        'I-PER': 2,
        'B-LOC': 3,
        'I-LOC': 4,
        'B-ORG': 5,
        'I-ORG': 6,
        'I-MISC': 7,
        'B-MISC': 8,
        }

REVERSE_LABELS = {
        0: 'O',
        1: 'B-PER',
        2: 'I-PER',
        3: 'B-LOC',
        4: 'I-LOC',
        5: 'B-ORG',
        6: 'I-ORG',
        7: 'I-MISC',
        8: 'B-MISC'
        }


class Sentence:
    """The class for sentence.
    """
    def __init__(self, labels, words, poss, nerdic):
        if len(words) != len(poss) or len(labels) != len(words):
            raise Exception('Words and poss are not matched !')
        self._labels = labels
        self._words = words
        self._poss = poss
        self._nerdic = nerdic
        self._predict = None
        self._maps = {
                'word': self._word,
                'poscon': self._poscon,
                'lexcon': self._lexcon,
                'bothcon': self._bothcon,
                }

    ########################################################
    # Public methods
    ########################################################
    def generate_keys(self, ftype):
        """Generate the feature keys based on the ftype.
        """
        reval = []
        for i in range(len(self._words)):
            reval.append(self._maps[ftype](i))

        return reval

    def generate_features(self, ftype):
        """Generate the feature indexs based on the ftype.
        """
        reval = []
        feat_keys = self.generate_keys(ftype)

        for label, vector in zip(self._labels, feat_keys):
            tmp = [self._nerdic[key] for key in vector]
            tmp = sorted(tmp)
            reval.append((LABELS[label], tmp))

        return reval

    def add_predict(self, label_ids):
        """Add the predict label for the current sentences.
        """
        self._predict = [REVERSE_LABELS[v] for v in label_ids]

    ########################################################
    # Property methods
    ########################################################
    @property
    def labels(self):
        reval = [LABELS[i] for i in self._labels]
        return reval

    @property
    def poss(self):
        return self._poss[:]

    @property
    def words(self):
        return self._words[:]

    ########################################################
    # Magic methods
    ########################################################
    def __len__(self):
        return len(self._words)

    def __repr__(self):
        words = self._words
        labels = self._labels
        poss = self._poss
        predict = self._predict

        ss = []
        if predict is not None:
            for word, pos, label, pred in zip(words, poss, labels, predict):
                s = ' '.join([word, pos, label, pred])
                ss.append(s)
            ss = '\n'.join(ss)
            ss += '\n\n'
        else:
            for word, pos, label in zip(words, poss, labels):
                s = ' '.join([word, pos, label])
                ss.append(s)
            ss = '\n'.join(ss)
            ss += '\n\n'
        return ss

    ########################################################
    # Private methods
    ########################################################
    def _word(self, index):
        """Generate the key for ftype word.

        Args:
            index: int - The index of the word

        Returns:
            list(str): The feature keys for the words
        """
        if index < -1 or index >= len(self._words):
            raise Exception('Invalid index !')
        if index >= 0 and index < len(self._words):
            key = 'curr-' + self._words[index] + '-word'
            if key not in self._nerdic:
                key = 'curr-UNKWORD'
        return [key]

    # def _wordcap(self, index):
    #     key = self._word(index)
    #     word = self._words[index]
    #     if word[0].isupper() is True:
    #         key.append(CAP)
    #     return key

    def _others(self, index):
        key = self._word(index)
        word = self._words[index]
        # Inital caps
        if word[0].isupper() is True:
            key.append('$init-caps$')
        # All caps
        if word.isupper() is True:
            key.append('$all-caps$')
        # Contains digitals
        val = [w.isdigit() for w in word]
        if bool(sum(val)) is True:
            key.append('$contains-dig$')
        # all digital
        if word.isdigit() is True:
            key.append('$all-dig$')
        # punc makrs
        marks = [',', '?', '!', '@', '#', '$', '%', '^',
                 '&', '*', '(', ')', '[', ']']
        for m in marks:
            if m in word:
                key.append('$punc-mark$')
                break
        # contains dots
        if '.' in word:
            key.append('$contains-dots$')
        # hypen
        if '-' in word:
            key.append('$contains-hypen$')
        if len(word) == 1:
            key.append('$single-char$')
        return key

    def _poscon(self, index):
        key = self._others(index)

        if index - 1 <= -1:
            t = 'prev-PHIPOS'
        else:
            t = 'prev-' + self._poss[index-1] + '-pos'
            if t not in self._nerdic:
                t = 'prev-UNKPOS'
        key.append(t)

        if index - 2 <= -1:
            t = 'prev2-PHIPOS'
        else:
            t = 'prev2-' + self._poss[index-2] + '-pos'
            if t not in self._nerdic:
                t = 'prev2-UNKPOS'
        key.append(t)

        if index + 1 == len(self._words):
            t = 'next-OMEGAPOS'
        else:
            t = 'next-' + self._poss[index+1] + '-pos'
            if t not in self._nerdic:
                t = 'next-UNKPOS'
        key.append(t)

        if index + 2 >= len(self._words):
            t = 'next2-OMEGAPOS'
        else:
            t = 'next2-' + self._poss[index+2] + '-pos'
            if t not in self._nerdic:
                t = 'next2-UNKPOS'
        key.append(t)
        return key

    def _lexcon(self, index):
        key = self._others(index)

        if index - 1 == -1:
            t = 'prev-PHI'
        else:
            t = 'prev-' + self._words[index-1] + '-word'
            if t not in self._nerdic:
                t = 'prev-UNKWORD'
        key.append(t)

        if index - 2 <= -1:
            t = 'prev2-PHI'
        else:
            t = 'prev2-' + self._words[index-2] + '-word'
            if t not in self._nerdic:
                t = 'prev2-UNKWORD'
        key.append(t)

        if index + 1 == len(self._words):
            t = 'next-OMEGA'
        else:
            t = 'next-' + self._words[index+1] + '-word'
            if t not in self._nerdic:
                t = 'next-UNKWORD'
        key.append(t)

        if index + 2 >= len(self._words):
            t = 'next2-OMEGA'
        else:
            t = 'next2-' + self._words[index+2] + '-word'
            if t not in self._nerdic:
                t = 'next2-UNKWORD'
        key.append(t)
        return key

    def _bothcon(self, index):
        key1 = self._poscon(index)
        key2 = self._lexcon(index)

        key = set(key1) | set(key2)
        return list(key)


class NERDic:
    """Dictionary class for NER task.
    """
    def __init__(self, train_path):
        """Construct a new NER features.

        Args:
            train_path: str - The path of training set.
        """
        self._train_path = train_path
        self._word_num = -1
        self._pos_num = -1

        word, pos = self._read_wordpos(train_path)
        self._word_num = len(word)
        self._pos_num = len(pos)

        self._dic = self._generate_dicts(word, pos)

        # for key, value in self._dic.items():
        #     s = ':'.join([key, str(value)])
        #     print(s)

    def max_id(self):
        """Reuturn the max id number.
        """
        return max(self._dic.values())

    ########################################################
    # Property
    ########################################################
    @property
    def distinct_word_num(self):
        return self._word_num

    @property
    def distinct_pos_num(self):
        return self._pos_num

    ########################################################
    # Magic methods
    ########################################################
    def __getitem__(self, key):
        return self._dic[key]

    def __contains__(self, key):
        return key in self._dic

    def __iter__(self):
        for key in self._dic:
            yield key

    ########################################################
    # Private methods
    ########################################################
    def _read_wordpos(self, path):
        """Read all the distinct words and pos.

        Args:
            path: str - The path of training data.

        Returns:
            words: The set of word
            poss: The set of pos
        """
        words = set()
        poss = set()
        with open(path, encoding='latin-1') as f:
            for line in f:
                if len(line.strip()) == 0:
                    continue
                s = line.strip().split()
                pos = s[1].strip()
                word = s[0].strip()

                words.add(word)
                poss.add(pos)
        return words, poss

    def _key(self, position, string, mode):
        """Generate the key for current string.

        Args:
            position: str - The position of the current string.
            string: str - the word/pos
            mode: str - word/pos
        """
        return ''.join([position, string, mode])

    def _constant_word(self):
        """Generate the contant keys.

        Return:
            list(str)
        """
        keys = []
        for p in POSITIONS:
            for m in WORDS:
                key = self._key(p, m, '')
                keys.append(key)
        return keys

    def _constant_pos(self):
        """Generate the contant keys.

        Return:
            list(str)
        """
        keys = []
        for p in POSITIONS:
            for m in POS:
                key = self._key(p, m, '')
                keys.append(key)
        return keys

    def _generate_dicts(self, words, poss):
        """Generate the dictionary from words and poss.
        Args:
            words: set - A set of distinct words.
            poss: set - A set of distinct poss.

        Return:
            a dictionary.
        """
        dic = collections.OrderedDict()

        # The index should starts from 1
        dic['x'] = len(dic)
        for w in words:
            for p in POSITIONS:
                # Current word
                key = self._key(p, w, '-word')
                dic[key] = len(dic)
        # Constant
        keys = self._constant_word()
        for key in keys:
            dic[key] = len(dic)

        for p in poss:
            for pp in POSITIONS:
                # Current pos
                key = self._key(pp, p, '-pos')
                dic[key] = len(dic)
        keys = self._constant_pos()
        for key in keys:
            dic[key] = len(dic)

        for key in OTHERS:
            dic[key] = len(dic)
        return dic
