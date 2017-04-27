# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-03-01 13:29:29
# Last modified: 2017-03-01 19:30:02

"""
Main entrance of the dirt algorithm.
"""

import sys

from utils import IOManager
from utils import Extractor
from database import Database
from similarity import Similarity


class DIRT:
    def __init__(self):
        self.IO = IOManager()
        self.exactor = Extractor('illegal.txt')

    def _construct_database(self, corpus_path):
        """Construct the database based on the corpus.

        Args:
            corpus_path: str - The path of corpus.

        Returns:
            Database
        """
        database = Database()
        # construct the database
        for words, poss in self.IO.read_sentences(corpus_path):
            triples = self.exactor.extract(words, poss)
            for triple in triples:
                database.insert(triple)

        return database

    def run(self, corpus_path, test_path, minfreq):
        self._database = self._construct_database(corpus_path)
        before_unique, before_total = self._stas(self._database)
        self._database.apply_minfreq(minfreq)
        after_unique, after_total = self._stas(self._database)
        sim = Similarity(self._database)
        test_phrases = self.IO.read_phrases(test_path)

        with open('trace.txt', 'w', encoding='utf8') as f:
            # Write the head line.
            args = [before_unique, after_unique, before_total, after_total]
            f.write('\n')
            self._write_head(f, args)

            for phrase in test_phrases:
                most_similar = self._find_k_similar(phrase, sim, 5)
                self._write_result(f, phrase, most_similar)

    def _stas(self, database):
        """Return the statistic of the database.
        """
        return len(database), database.path_number()

    def _write_head(self, f, args):
        """Write the head line for output.
        """
        s = 'Found {a} distinct paths, {b} after minfreq filtering.\n'
        s = s.format(a=args[0], b=args[1])
        f.write(s)

        s = 'Found {a} path instances, {b} after minfreq filtering.\n'
        s = s.format(a=args[2], b=args[3])
        f.write(s)
        f.write('\n')

    def _find_k_similar(self, phrase, sim, k=5):
        """Find the k most similar paths.

        If phrase does not in the database,  reutrn None

        Args:
            phrase: str
            sim: Similarity
            k: int

        Returns:
            a list of tuple with size of k.
            Each tuple contains the path and corrsponding score.
        """
        if phrase not in self._database:
            return None

        reval = [(path, sim.PathSim(phrase, path)) for path in self._database]
        reval.sort(key=lambda x: x[-1], reverse=True)
        # To deal with tie cases.
        value = reval[k-1][-1]
        reval = [v for v in reval if v[-1] >= value]
        return reval

    def _write_result(self, f, phrase, result):
        """Write thr result into files.

        Args:
            f: file
            phrase: str
            result: list(tuple(path, score))
        """
        s = 'MOST SIMILAR RULES FOR: {a}\n'.format(a=phrase)
        n = 'This phrase is not in the triple database.\n'
        t = '{a}. {b}\t{c}\n'
        f.write(s)
        if result is None:
            f.write(n)
        else:
            for i, item in enumerate(result):
                path = str(item[0])
                score = str(item[-1])
                tt = t.format(a=str(i+1), b=path, c=score)
                f.write(tt)
        f.write('\n')


if __name__ == '__main__':
    runner = DIRT()
    corpus_path = sys.argv[1]
    test_path = sys.argv[2]
    minfreq = int(sys.argv[3])
    runner.run(corpus_path, test_path, minfreq)
