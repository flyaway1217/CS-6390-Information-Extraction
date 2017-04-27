# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-03-03 10:45:13
# Last modified: 2017-04-13 11:42:21

"""
Main entrance fo the NER system.
"""

import numpy as np
from scipy.sparse import csr_matrix

from utils import IOManager
from sentence import NERDic
from sentence import Sentence
from learner import Learner
import sentence
from viterbi import Viterbi


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
    def __init__(self, max_iter=100):
        self._io = IOManager()
        self._learners = []
        for i in range(len(sentence.REVERSE_LABELS)):
            self._learners.append(Learner(max_iter=max_iter))

    def train(self, train_path, ftype):
        """Train the NER model.

        Args:
            train_path: str - The path of training set.
            ftype: str - Indicating the feature type.
        """
        self._nerdic = NERDic(train_path)
        io = self._io
        sentences = []

        # reading the training set.
        for words, poss, labels in io.read_sentences(train_path):
            sentences.append(Sentence(labels, words, poss, self._nerdic))

        feats, labels = self._prepare_feats(sentences, ftype)

        sep_labels = []
        for i in sentence.REVERSE_LABELS.keys():
            sep_labels.append([])
            for label in labels:
                if label == i:
                    sep_labels[i].append(1)
                else:
                    sep_labels[i].append(0)

        print('Start first phase training...')
        for i, learner in enumerate(self._learners):
            learner.train(feats, sep_labels[i])

        # print('Start second phase training...')
        # second_feats = []
        # for learner in self._learners:
        #     second_feats.append(learner.confidence(feats))
        # second_feats = np.array(second_feats)
        # second_feats = second_feats.transpose()

        # self._second_learner = Learner(max_iter=1000)
        # self._second_learner.train(second_feats, labels)

    def predict(self, test_path, output_path, ftype):
        """Predict the test set.

        Args:
            test_path: str - The path of test set.
            output_path: str - The path of output file.
            ftype: str - Indicating the feature type.

        Return:
            list(Sentence) - The sentence with predicted labels.
        """
        # reading the training set.
        io = self._io
        sentences = []
        for words, poss, labels in io.read_sentences(test_path):
            sentences.append(Sentence(labels, words, poss, self._nerdic))

        for sent in sentences:
            feats, labels = self._prepare_feats([sent], ftype)
            confidence = []
            predict_ids = []
            for learner in self._learners:
                confidence.append(learner.confidence(feats))

            confidence = np.array(confidence)
            confidence = confidence.transpose()

            for con in confidence:
                predict_ids.append(np.argmax(con))

            # predict_ids = self._second_learner.predict(confidence)
            sent.add_predict(predict_ids)

        io.write_sentences(output_path, sentences)

    def _prepare_feats(self, sentences, ftype):
        """Prepare the feartures

        Args:
            sentences: list(Sentence)
            ftype: str - Indicating the type of features.

        Return:
            lables: list(str)
            feats: scipy.sparse.csr_matrix
        """
        # Extracting the features
        labels = []
        feats = []
        for sent in sentences:
            # items = sent.generate_keys(ftype)
            # print(items[5])
            # exit()
            items = sent.generate_features(ftype)
            for label, feat in items:
                labels.append(label)
                feats.append(feat)
        # Prepare for the scipy spase format.
        rows = []
        cols = []
        data = []
        for i in range(len(feats)):
            for v in feats[i]:
                rows.append(i)
                cols.append(v)
                data.append(1)
        M = len(feats)
        N = self._nerdic.max_id() + 1
        feats = csr_matrix((data, (rows, cols)), shape=(M, N),
                           dtype=np.float64)

        return feats, labels

    def viterbi(self, train_path, test_path, output_path):

        self._nerdic = NERDic(train_path)
        io = self._io
        train_sentences = []
        test_sentences = []
        for words, poss, labels in io.read_sentences(train_path):
            train_sentences.append(Sentence(labels, words, poss, self._nerdic))

        for words, poss, labels in io.read_sentences(test_path):
            test_sentences.append(Sentence(labels, words, poss, self._nerdic))

        viterbi = Viterbi(9)
        viterbi.train(train_sentences)
        for sent in test_sentences:
            predict_ids = viterbi.search(sent)
            sent.add_predict(predict_ids)

        io.write_sentences(output_path, test_sentences)

if __name__ == '__main__':
    ner = NER(1000)
    train_path = '../data/esp.train'
    test_path = '../data/esp.testb'
    output_path = '../bin/output_viterbi.txt'

    # ner.train(path, 'bothcon')
    # print('Start predicting...')
    # ner.predict('../data/esp.testb', '../bin/output_basic.txt', 'bothcon')
    ner.viterbi(train_path, test_path, output_path)
