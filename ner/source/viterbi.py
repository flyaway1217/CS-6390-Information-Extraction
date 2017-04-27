# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-04-10 10:44:29
# Last modified: 2017-04-13 12:11:11

"""
Implement the Viterbi algorithm.
"""

import numpy as np

START = '#S'
END = '#E'


class Viterbi:
    """Viterbi class.
    """
    def __init__(self, label_size):
        """Construct a new Viterbi class.

        Args:
            sentences: list(sentence)
        """
        self._trans = dict()
        self._emit = dict()
        self._label_size = label_size

    def train(self, sentences):
        """Extracting the probability distribution
            from sentences.
        Args:
            sentences: list(Sentence)
        """
        for sent in sentences:
            # For transition probabilities
            labels = sent.labels
            labels.insert(0, START)
            labels.append(END)
            for index in range(1, len(labels)):
                key = labels[index-1]
                value = labels[index]
                if key not in self._trans:
                    self._trans[key] = dict()
                self._trans[key][value] = self._trans[key].get(value, 0) + 1

            # For emit probabilities.
            labels = sent.labels
            poss = sent.poss
            words = sent.words
            for label, pos, word in zip(labels, poss, words):
                key = label
                value = '|'.join([word, pos])
                if key not in self._emit:
                    self._emit[key] = dict()
                self._emit[key][value] = self._emit[key].get(value, 0) + 1

    def search(self, sentence):
        """Run the viterbi algorihtm
            to search for the best sequence.
        """
        n = len(sentence)
        words = sentence.words
        poss = sentence.poss

        # Initialize the table
        # table size: label_size * n
        table = []
        back = []
        for _ in range(self._label_size):
            table.append([None]*n)
            back.append([None]*n)

        for t in range(self._label_size):
            word = '|'.join([words[0], poss[0]])
            table[t][0] = self._get_trans(START, t) * self._get_emit(t, word)
            back[t][0] = 0

        for index in range(1, len(words)):
            word = '|'.join([words[index], poss[index]])
            for t in range(self._label_size):
                m = float('-INF')
                maxj = -1
                for j in range(self._label_size):
                    prob = table[j][index-1] * self._get_trans(j, t)
                    if prob > m:
                        prob = m
                        maxj = j
                table[t][index] = self._get_emit(t, word) * m
                back[t][index] = maxj

        # Recover the sequence label
        seq = [None] * n
        score = [table[j][n-1] for j in range(len(self._label_size))]
        seq[n-1] = np.argmax(score)

        for i in range(n-2, -1, -1):
            seq[i] = back[seq[i+1]][i+1]
        return seq

    def _get_emit(self, label, word):
        """Generate the emit probability.

        Args:
            label: int - The label.
            word: str - The word and pos tag.
        """
        denominator = 0
        for key in self._emit[label]:
            denominator += self._emit[label][key]

        return self._emit[label][word] / denominator

    def _get_trans(self, pre_label, post_label):
        """Generate the trnas probability.

        Args:
            pre_label: {int, str} - The last label.
            post_label: int - The currnt label.
        """
        denominator = 0
        for key in self._trans[pre_label]:
            denominator += self._trans[pre_label][key]
        A = self._trans[pre_label].get(post_label, 0) + 1
        return A / (denominator+self._label_size)
