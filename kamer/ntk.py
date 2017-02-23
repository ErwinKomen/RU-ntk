#! /usr/bin/env python3
# -*- coding: utf8 -*-

import os.path
import xml.etree.ElementTree as ET
import re
from sentiana import SentiAna

# ----------------------------------------------------------------------------------
# Name :    ntk
# Goal :    Methods supporting working with NTK xml files
# History:
# 16/feb/2017    ERK Created
# ----------------------------------------------------------------------------------
class ntk:
    """Methods supporting processing NTK xml files"""

    adv = None
    method = ""
    lines = ""
    snt = None
    lUtt = []

    # ======================= CLASS INITIALIZER ========================================
    def __init__(self, oErr, sMethod, sLines):
        # Set the error handler
        self.errHandle = oErr
        self.rePunct = re.compile(r"[\.\,\?\!\'\"\`\;\:\-]")
        self.reLineEnd = re.compile(r"[\.\?\!]")
        self.reNalpha = re.compile(r"[^\w]")
        self.method = sMethod
        self.lines = sLines
        # Create a sentiment object
        self.snt = SentiAna(oErr)


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

            # ======== DEBUGGING
            #if "h-tk-20102011-5-31.xml" in flInput:
            #    i = 0
            # ==================

            # Remove first lines until first < starts
            iFirst = -1
            iLen = len(lLine)
            for i in range(len(lLine)):
                sLine = lLine[i]
                if "<" in sLine[0:2]:
                    iFirst = i
                    break
            if iFirst >= 0:
                # Slice the input array
                lLine = lLine[iFirst:iLen]
            sText = "\n".join(lLine)
            # Parse the text
            try:
                root = ET.fromstring(sText)
            except:
                # act
                self.errHandle.DoError("ntk/load parser exception")
                return None
            
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
    def getUtteranceList(self, doc, fName, oAdv):
        """Retrieve a list of utterance objects from the doc tree"""
        
        self.lUtt = []       # List of utterances
        sXmlType = ""   # Kind of XML document we are processing

        try:
            # Make sure the adverb object is tied
            self.adv = oAdv

            # Get the root name, which determines how we will process
            sRootType = doc.tag.lower()
            # Get basic facts
            if sRootType == "handeling":
                sXmlType = "a"
            elif sRootType == "officiele-publicatie":
                sXmlType = "b"
            else:
                # We don't know the XML type
                self.errHandle.Status("The XML type of this document is not known")
                return None

            # Get basic facts
            if sXmlType == "a":
                frontm = doc.find("frontm")
                vergjaar = frontm.find("vergjaar").text
                # get a list of years from...to
                lstYears = re.findall(r"\d\d\d\d", vergjaar)
            elif sXmlType == "b":
                # Extract the year as the first 4 numbers from the file name in metadata > meta > @content
                meta = doc.find("metadata").find("meta")
                content = meta.attrib['content']
                # get a list of years from...to
                lstYears = re.findall( r"\d\d\d\d", content)
                # vergjaar = "-".join(lstYears)

            # Type A: Get to the part > item
            if sXmlType == "a":
                # Iterate over all <item> items
                for itempart in doc.find("part").iter("item"):
                    # Iterate over all the 
                    for spreker in itempart.iter("spreker"):
                        # note the spreker details
                        wie = spreker.find("wie")
                        aanspr = "(onbekend)"
                        partij = "(onbekend)"
                        elAanspr = wie.find("aanspr")
                        elPartij = wie.find("partij")
                        elErwin = wie.find("erwin")
                        if elAanspr != None:
                            aanspr = elAanspr.text
                        if elPartij != None:
                            partij = elPartij.text
                        # Iterate over all the utterances of this person
                        for al in spreker.iter("al"):
                            self.process_text(al, lstYears, aanspr, partij)
            elif sXmlType == "b":
                # Iterate over all <agendapunt> items
                for agendapunt in doc.find("handelingen").iter("agendapunt"):
                    # Iterate over all <spreekbeurt> objects
                    for spreekbeurt in agendapunt.iter("spreekbeurt"):
                        # Default values
                        aanspr = "(onbekend)"
                        partij = "(onbekend)"
                        # Get the spreker (there may only be ONE according to the DTD)
                        spreker = spreekbeurt.find("spreker")
                        # Retrieve voorvoegsels and achternaam
                        voorvoegsels = spreker.find("voorvoegsels").text
                        achternaam = spreker.find("naam").find("achternaam").text
                        # Note: we do NOT process the words of the Voorzitter
                        if achternaam != "voorzitter":
                            aanspr = voorvoegsels
                            # Try to retrieve the political party
                            politiek = spreker.find("politiek")
                            if politiek != None:
                                partij = politiek.text

                            # Iterate over the <al> elements i9n here
                            tekst = spreekbeurt.find("tekst")
                            for al in tekst.iter("al"):
                                self.process_text(al, lstYears, aanspr, partij)

            # Return the list of utterances
            return self.lUtt
        except:
            # act
            self.errHandle.DoError("ntk/getUtteranceList exception")
            return None

    # ----------------------------------------------------------------------------------
    # Name :    process_text
    # Goal :    Process one piece of <al> 
    # History:
    # 20/feb/2017    ERK Created
    # ----------------------------------------------------------------------------------
    def process_text(self, elAl, lstYears, aanspr, partij):
        """Process this piece of text"""

        try:
            # Find out the from and to year
            if len(lstYears) == 1:
                jaar_vanaf = lstYears[0]
                jaar_tot = lstYears[0]
            else:
                jaar_vanaf = lstYears[0]
                jaar_tot = lstYears[1]
            # Break up the utterance in lines
            sLine = elAl.text
            if sLine != None:
                # Change the newlines to spaces
                sLine = sLine.replace("\n", " ")
                sLine = sLine.replace("\r", "")
                # Divide the line into parts divided by sentence breakers [.], [?], [!]
                lLine = re.sub(self.reLineEnd, "\n", sLine).split(sep="\n")
                # lLine = sLine.split("\n")
                # Walk all lines
                for sText in lLine:
                    # Trim it
                    sText = sText.strip().strip("\n").strip("\r")

                    # double check if it is empty
                    if sText != "":
                    
                        # ------------------- DEBUG -----------------------------
                        #if "heel" in sText:
                        #    iStop = 1
                        # -------------------------------------------------------

                        # Tokenize the text into words on the basis of spaces, stripping off metadata
                        wList = re.sub(self.reNalpha, " ", sText).split()
                        # Get a new count object -- this is method-dependant
                        oCount = self.adv.getTypeCountObject(self.method)
                        # Walk the list of words
                        for wrd in wList:
                            # Make sure the word is lower-case
                            wrd = wrd.lower()
                            # Get a match for this word 
                            sType = self.adv.getType(wrd)
                            # Do we have a match?
                            if sType != "":
                                # Counting is method-dependant
                                if self.method == "compact":
                                    oCount[sType] += 1
                                elif self.method == "full":
                                    oCount[wrd] += 1

                        # Perform POS-tagging

                        # Either: (a) at least one match or (b) 'lines' option is 'all'
                        if self.lines == "all" or self.anyCountNonZero(oCount):
                            # Prepare one utterance object
                            oUtt = {}
                            oUtt['jaar_van'] = jaar_vanaf
                            oUtt['jaar_tot'] = jaar_tot
                            oUtt['aanspr'] = aanspr
                            oUtt['partij'] = partij
                            oUtt['s'] = sText
                            # Add 'Sentimentanalyse' scores
                            tPolSubj = self.snt.get_analysis(sText)
                            oUtt['polar'] = tPolSubj[0]     # first element of the tuple
                            oUtt['subj'] = tPolSubj[1]      # second element of the tuple

                            # TODO: implement 'intens'
                            # oUtt['intens'] = 0            # TODO: 

                            # Copy the counts
                            oUtt['count'] = oCount
                            # Add this object to the list
                            self.lUtt.append(oUtt)

            # Indicate all went well
            return True
        except:
            # act
            self.errHandle.DoError("ntk/process_text exception")
            return False



    # ----------------------------------------------------------------------------------
    # Name :    anyCountNonZero
    # Goal :    Check if any of the objects in [oCount] are non-zero
    # History:
    # 20/feb/2017    ERK Created
    # ----------------------------------------------------------------------------------
    def anyCountNonZero(self, oCount):
        """Check if any of the members is not zero"""

        # Iterate over all the objects in [oCount]
        for m in oCount:
            # Is this object non-zero
            if oCount[m] != 0:
                return True
        # Default: return false
        return False
