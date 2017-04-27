# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-02-28 13:43:07
# Last modified: 2017-03-01 17:02:35

"""
Database for DIRT
"""


class Path:
    """Path is the real data structure that store in the database.
    """
    def __init__(self, path, slotX, slotY):
        self._path = path
        self._slot = dict()

        self._slot['slotX'] = dict()
        self._slot['slotY'] = dict()

        self._slot['slotX'][slotX] = 1
        self._slot['slotY'][slotY] = 1

    ########################################################
    # Public methods
    ########################################################
    def insert(self, slotX, slotY):
        self.slotX[slotX] = self.slotX.get(slotX, 0) + 1
        self.slotY[slotY] = self.slotY.get(slotY, 0) + 1
        self._check()

    def slot(self, value):
        """Return the whole slot based on the given value.

        Args:
            value: str - 'SlotX' ot 'SlotY'
        """
        return self._slot[value]

    ########################################################
    # Property
    ########################################################
    @property
    def path(self):
        return self._path

    @property
    def slotX(self):
        return self._slot['slotX']

    @property
    def slotY(self):
        return self._slot['slotY']

    ########################################################
    # Magic methods
    ########################################################
    def __len__(self):
        """Return the total number of slots.
        """
        return sum([v for v in self.slotY.values()])

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)

    ########################################################
    # Private methods
    ########################################################
    def _check(self):
        """To make ure the number of slotX and slotY is equal
        """
        X = sum([v for v in self.slotX.values()])
        Y = sum([v for v in self.slotY.values()])

        assert X == Y


class Database:
    """Construct the Triple Database.

    As a database,  there should be some basic operations:

    Attributes:
        self_db: dict(path)

    - insert(): Insert a new item.
    - search(): Seach for a particular item.
    """
    def __init__(self):
        self._db = dict()

    def insert(self, triple):
        path = triple.path
        slotX = triple.slotX
        slotY = triple.slotY
        if triple.path not in self._db:
            ins = Path(path, slotX, slotY)
            self._db[path] = ins
        else:
            self._db[path].insert(slotX, slotY)

    def path_number(self):
        """Return the numbe of paths intotal.
        """
        values = sum([len(v) for v in self._db.values()])
        return values

    def apply_minfreq(self, k):
        paths = [p for p in self._db if len(self._db[p]) < k]
        for p in paths:
            del self._db[p]

    def search_counter(self, path=None, slot=None, filler=None):
        """Search the counter number based on the given path, slotX and slotY.

        Args:
            path: str
        """
        if path is None:
            inss = self._db.values()
        else:
            inss = [self._db[path]]

        if slot is None:
            raise Exception('Must given a slot name !')

        value = 0
        slots = [ins.slot(slot) for ins in inss]

        if filler is None:
            value += sum([sum(v.values()) for v in slots])
        else:
            value = sum([v.get(filler, 0) for v in slots])

        return value

    def search_words(self, path, slot):
        """Return all the words the fill the slot in path.

        Return:
            set(str)
        """
        ins = self._db[path]
        return set(ins.slot(slot).keys())

    ########################################################
    # Magic methods
    ########################################################
    def __len__(self):
        """Return the number of distinct paths.
        """
        return len(self._db)

    def __contains__(self, path):
        """Check if the given path is in the database.
        """
        return path in self._db

    def __iter__(self):
        return iter(self._db.keys())
