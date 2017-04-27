# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-02-21 10:29:21
# Last modified: 2017-02-21 10:42:39

"""
Calculate the statistics information of the given data set.
"""


def stat(path):
    with open(path, encoding='latin-1') as f:
        word_count = 0
        unique_words = set()
        sent_count = 0
        for line in f:
            if len(line.strip()) != 0:
                word_count += 1
                word = line.strip().split()[0]
                unique_words.add(word)
            else:
                sent_count += 1
    print('In the file {a}:\n'.format(a=path))
    print('There are {a} sentences.'.format(a=sent_count))
    print('There are {a} words in total.'.format(a=word_count))
    print('There are {a} unique words.'.format(a=str(len(unique_words))))

if __name__ == '__main__':
    # path = '../data/esp.train'
    # path = '../data/esp.testa'
    path = '../data/esp.testb'
    stat(path)
