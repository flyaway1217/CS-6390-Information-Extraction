# !/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Author: Flyaway - flyaway1217@gmail.com
# Blog: zhouyichu.com
#
# Python release: 3.4.5
#
# Date: 2017-03-03 10:43:42
# Last modified: 2017-04-09 16:20:18

"""
Wrapper for the classifier.
"""

from sklearn import svm
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.ensemble import AdaBoostClassifier


class Learner:
    """Classifier for the NER system.
    """
    def __init__(self, max_iter=100):
        """Construct a new classifier.

        Args:
            max_iter: int - The maximum iterations.
        """
        self._max_iter = max_iter

    def train(self, x, y):
        """Train the model using the featture x and label y.

        Args:
            x: scipy.sparse.csr_matrix - The features matrix in sparse format.
            y: list(int) - Labels for each instance.
        """
        self._clf = svm.LinearSVC(max_iter=self._max_iter,
                                  # class_weight='balanced',
                                  )
        # self._clf = RandomForestClassifier(n_estimators=40, n_jobs=-1)
        # self._clf = AdaBoostClassifier(n_estimators=100)
        self._clf.fit(x, y)

    def predict(self, feats):
        """Predict the label based on the features.

        Args:
            feats: scipy.sparse.csr_matrix - The features matrix
                   in sparse format.

        Returns:
            list(int)
        """
        predict = self._clf.predict(feats)
        return predict

    def confidence(self, feats):
        """Predict the confidence for each class.

        Args:
            feats: scipy.sparse.csr_matrix - The features matrix
                   in sparse format.

        Returns:
            list(int)
        """
        confidence = self._clf.decision_function(feats)
        # confidence = self._clf.predict_proba(feats)
        # confidence = [max(v) for v in confidence]
        return confidence
