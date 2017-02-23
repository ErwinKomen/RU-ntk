#! /usr/bin/env python3
# -*- coding: utf8

# from pattern.text.nl import sentiment # parse, split, sentiment
from pattern.text.nl import sentiment
# import text.nl

class SentiAna:
    """Sentiment analyse"""

    method = "pattern"      # The method to be taken

    # ======================= CLASS INITIALIZER ========================================
    def __init__(self, oErr):
        # Initialize a local array of word-elements
        self.errHandle = oErr

    def get_analysis(self, sSent):
        """Return the sentiment-analysis of one sentence"""

        try:
            score = sentiment(sSent)
            return score
        except: 
            # act upon error
            self.errHandle.DoError("SentiAna/get_analysis")
            return None
