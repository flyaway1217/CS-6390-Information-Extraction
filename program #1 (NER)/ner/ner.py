# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-01-27 11:24:44
# Last modified: 2017-02-06 20:18:32

"""
Extracting features for NER task.
"""

import collections
import sys


POSITIONS = ['curr-', 'prev-', 'next-']
WORDS = ['PHI', 'OMEGA', 'UNKWORD']
POS = ['PHIPOS', 'OMEGAPOS', 'UNKPOS']
CAP = '$capitalized$'

LABELS = {
        'O': 0,
        'B-PER': 1,
        'I-PER': 2,
        'B-LOC': 3,
        'I-LOC': 4,
        'B-ORG': 5,
        'I-ORG': 6,
        }


class NER:
    """ Extracting features from the given training and test set.
    There are 5 different modes:

    1.word: use only the word w itself as a feature
    2.wordcap: use the word w itself as a feature,
               and create a binary feature that indicates
               whether w is capitalized
    3.poscon: in addition to the wordcap features,
              create context features for the POS tag of
              the previous word w−1 and the POS tag of the following word w+1
    4.lexcon: in addition to the wordcap features,
              create context features for the string of the
              previous word w−1 and the following word w+1
    5.bothcon: use ALL of the features above: the wordcap features,
               the POS context features, and the lexical context features.
    """
    def __init__(self, train_path, test_path, ftype):
        self._train_path = train_path
        self._test_path = test_path
        self._ftype = ftype
        self._nerdic = NERDic(self._train_path)

    def run(self):

        # For the train file
        sentences = self._read_sentence(self._train_path)
        training_num = [len(sent) for sent in sentences]
        training_num = sum(training_num)
        outpath = '.'.join([self._train_path, self._ftype])
        self._write_sentences(outpath, sentences)

        # For the test file
        sentences = self._read_sentence(self._test_path)
        test_num = [len(sent) for sent in sentences]
        test_num = sum(test_num)
        outpath = '.'.join([self._test_path, self._ftype])
        self._write_sentences(outpath, sentences)

        print('Found {a} training instances with {b} distinct words'
              'and {c} distinct POS tags'.format(
                  a=str(training_num),
                  b=str(self._nerdic.distinct_word_num),
                  c=str(self._nerdic.distinct_pos_num)))
        print('Found {a} test instances'.format(a=str(test_num)))

    def _write_sentences(self, path, sentences):
        with open(path, 'w', encoding='utf8') as f:
            for sent in sentences:
                for label, feats in sent.generate_features(self._ftype):
                    label = str(label)
                    feats = [str(v)+':1' for v in feats]
                    f.write(' '.join([label]+feats))
                    f.write('\n')
                # f.write('\n')

    def _read_sentence(self, path):
        reval = []
        with open(path, encoding='utf8') as f:
            labels = []
            words = []
            poss = []
            for line in f:
                if len(line.strip()) == 0:
                    reval.append(Sentence(labels, words, poss, self._nerdic))
                    labels = []
                    words = []
                    poss = []
                else:
                    s = line.split()
                    labels.append(s[0].strip())
                    words.append(s[2].strip())
                    poss.append(s[1].strip())
            if len(labels) != 0:
                reval.append(Sentence(labels, words, poss, self._nerdic))
        return reval


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
        self._maps = {
                'word': self._word,
                'wordcap': self._wordcap,
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

    ########################################################
    # Magic methods
    ########################################################
    def __len__(self):
        return len(self._words)

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

    def _wordcap(self, index):
        key = self._word(index)
        word = self._words[index]
        if word[0].isupper() is True:
            key.append(CAP)
        return key

    def _poscon(self, index):
        key = self._wordcap(index)

        if index - 1 == -1:
            t = 'prev-PHIPOS'
        else:
            t = 'prev-' + self._poss[index-1] + '-pos'
            if t not in self._nerdic:
                t = 'prev-UNKPOS'
        key.append(t)

        if index + 1 == len(self._words):
            t = 'next-OMEGAPOS'
        else:
            t = 'next-' + self._poss[index+1] + '-pos'
            if t not in self._nerdic:
                t = 'next-UNKPOS'
        key.append(t)
        return key

    def _lexcon(self, index):
        key = self._wordcap(index)

        if index - 1 == -1:
            t = 'prev-PHI'
        else:
            t = 'prev-' + self._words[index-1] + '-word'
            if t not in self._nerdic:
                t = 'prev-UNKWORD'
        key.append(t)

        if index + 1 == len(self._words):
            t = 'next-OMEGA'
        else:
            t = 'next-' + self._words[index+1] + '-word'
            if t not in self._nerdic:
                t = 'next-UNKWORD'
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
        with open(path, encoding='utf8') as f:
            for line in f:
                if len(line.strip()) == 0:
                    continue
                s = line.strip().split()
                pos = s[1].strip()
                word = s[-1].strip()

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
        dic[CAP] = len(dic)
        return dic


if __name__ == '__main__':
    # train_path = './train.txt'
    # test_path = './test.txt'

    # ner = NER(train_path, test_path, 'bothcon')
    # ner.run()

    train_path = sys.argv[1]
    test_path = sys.argv[2]
    ftype = sys.argv[3]
    ner = NER(train_path, test_path, ftype)
    ner.run()
