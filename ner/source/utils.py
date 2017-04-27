# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-03-03 10:22:46
# Last modified: 2017-03-04 10:17:10

"""
Basic operations for a NER system.
"""


class IOManager:
    """IO class.
    """
    def __init__(self):
        pass

    def read_sentences(self, path):
        """Read the sentences.

        Args:
            path: str - The corpus path.

        Yields:
            words: list(str)
            poss: list(str)
            labels: list(str)
        """
        with open(path, encoding='latin-1') as f:
            words = []
            poss = []
            labels = []
            for line in f:
                if len(line.strip()) == 0:
                    yield words, poss, labels
                    words = []
                    poss = []
                    labels = []
                    continue
                s = line.strip().split()
                words.append(s[0].strip())
                poss.append(s[1].strip())
                labels.append(s[2].strip())

    def write_sentences(self, path, sentences):
        """Write the sentences into file.

        Args:
            path:str -  The path of output file.
        """
        with open(path, 'w', encoding='latin-1') as f:
            for sent in sentences:
                f.write(str(sent))

if __name__ == '__main__':
    path = '../data/esp.train'
    io = IOManager()
    for words, poss, labels in io.read_sentences(path):
        print(words)
        print(poss)
        print(labels)
