# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-02-28 13:39:46
# Last modified: 2017-03-01 13:52:37

"""
Calculate the similiariy between two paths.
"""

import math


class Similarity:
    """The class to calculate similarity between paths.
    """
    def __init__(self, database):
        self._database = database

    def _MI(self, path, slot, filler):
        """Calculate the MI value

        Args:
            path: str - The path string.
            slot: str - 'SlotX' or 'SlotY'
            filler: str - The fill word.

        Return:
            float
        """
        A = self._database.search_counter(path=path,
                                          slot=slot,
                                          filler=filler)
        B = self._database.search_counter(slot=slot)
        C = self._database.search_counter(path=path,
                                          slot=slot)
        D = self._database.search_counter(slot=slot,
                                          filler=filler)
        if C*D == 0:
            return 0
        value = math.log2((A*B)/(C*D))
        if value < 0:
            return 0
        return value

    def _slot_sim(self, pathA, pathB, slot):
        """Calculate the slot similarity based on the given paths.

        Args:
            pathA: str
            pathB: str
            slot: str - 'SlotX' or 'SlotY'

        Return:
            float
        """
        wordsA = self._database.search_words(pathA, slot)
        wordsB = self._database.search_words(pathB, slot)
        common = wordsA & wordsB
        A = 0
        for word in common:
            A += (self._MI(pathA, slot, word) + self._MI(pathB, slot, word))

        B = 0
        for word in wordsA:
            B += self._MI(pathA, slot, word)
        for word in wordsB:
            B += self._MI(pathB, slot, word)

        return A/B

    def PathSim(self, pathA, pathB):
        A = self._slot_sim(pathA, pathB, 'slotX')
        B = self._slot_sim(pathA, pathB, 'slotY')
        return math.sqrt(A*B)
