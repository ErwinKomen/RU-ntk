#! /usr/bin/env python3
# -*- coding: utf8 -*-

import os.path
import xml.etree.ElementTree as ET
import re

# ----------------------------------------------------------------------------------
# Name :    ntk
# Goal :    Methods supporting working with NTK xml files
# History:
# 16/feb/2017    ERK Created
# ----------------------------------------------------------------------------------
class ntk:
    """Methods supporting processing NTK xml files"""

    # ======================= CLASS INITIALIZER ========================================
    def __init__(self, oErr):
        # Set the error handler
        self.errHandle = oErr
        self.rePunct = re.compile(r"[\.\,\?\!\'\"\`\;\:\-]")
        self.reNalpha = re.compile(r"[^\w]")


    # ----------------------------------------------------------------------------------
    # Name :    load
    # Goal :    Read an NTK xml file
    # History:
    # 16/feb/2017    ERK Created
    # ----------------------------------------------------------------------------------
    def load(self, flInput):
        """Load (read) an XML file"""
        lLine = []

        try:
            # Validate: does flInput exist?
            if (not os.path.isfile(flInput)) : 
                self.errHandle.DoError("Input file not found: " + flInput)
                return None

            # Load the input document into an array
            with open(flInput, encoding="utf8") as f:
                lLine = f.readlines()

            # Remove first lines until first < starts
            iFirst = -1
            iLen = len(lLine)
            for i in range(len(lLine)):
                sLine = lLine[i]
                if "<" in sLine[1:2]:
                    iFirst = i
                    break
            if iFirst >= 0:
                # Slice the input array
                lLine = lLine[iFirst:iLen]
            sText = "\n".join(lLine)
            # Parse the text
            root = ET.fromstring(sText)
            
            # Return what we have
            return root
        except:
            # act
            self.errHandle.DoError("ntk/load exception")
            return None

    # ----------------------------------------------------------------------------------
    # Name :    getUtteranceList
    # Goal :    Get a list of utterance objects containing one or more adverbs
    # History:
    # 16/feb/2017    ERK Created
    # ----------------------------------------------------------------------------------
    def getUtteranceList(self, doc, oAdv):
        """Retrieve a list of utterance objects from the doc tree"""

        lUtt = []
        try:
            # Get basic facts
            frontm = doc.find("frontm")
            vergjaar = frontm.find("vergjaar").text

            # Get to the part > item
            # itempart = doc.find("part").find("item")
            for itempart in doc.find("part").iter("item"):
                # Iterate over all the 
                for spreker in itempart.iter("spreker"):
                    # note the spreker details
                    wie = spreker.find("wie")
                    aanspr = "m"
                    partij = ""
                    elAanspr = wie.find("aanspr")
                    elPartij = wie.find("partij")
                    elErwin = wie.find("erwin")
                    if elAanspr != None:
                        aanspr = elAanspr.text
                    if elPartij != None:
                        partij = elPartij.text
                    # Iterate over all the utterances of this person
                    for al in spreker.iter("al"):
                        # Break up the utterance in lines
                        lLine = al.text.split("\n")
                        # Walk all lines
                        for sText in lLine:
                            # Tokenize the text into words on the basis of spaces, stripping off metadata
                            wList = re.sub(self.reNalpha, " ", sText).split()
                            oCount = {"arm": 0, "rijk": 0}
                            # Walk the list of words
                            for wrd in wList:
                                # Get a match for this word 
                                sType = oAdv.getType(wrd)
                                # Do we have a match?
                                if sType != "":
                                    oCount[sType] += 1
                            # Do we have at least one match?
                            if oCount["arm"] > 0 or oCount["rijk"] > 0:
                                # Prepare one utterance object
                                oUtt = {}
                                oUtt['jaar'] = vergjaar
                                oUtt['aanspr'] = aanspr
                                oUtt['partij'] = partij
                                oUtt['s'] = sText
                                oUtt['arm'] = oCount["arm"]
                                oUtt['rijk'] = oCount["rijk"]
                                # Add this object to the list
                                lUtt.append(oUtt)

            # Return the list of utterances
            return lUtt
        except:
            # act
            self.errHandle.DoError("ntk/getUtteranceList exception")
            return None
