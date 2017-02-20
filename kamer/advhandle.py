import io, os, json

class AdvHandle:
    """Handle intensifying adverbs"""

    loc_words = []
    loc_types = []
    errHandle = None

    # ======================= CLASS INITIALIZER ========================================
    def __init__(self, oErr):
        # Initialize a local array of word-elements
        self.loc_words = []
        self.errHandle = oErr

    def Load(self, fThis):
        """Load a json file into the loc_words list"""

        try:
            # Load intensifiers from the JSON list
            if (os.path.isfile(fThis)):
                # This is a file, load it into an object as json
                with open(fThis) as json_data:
                    oData = json.load(json_data)
                    json_data.close()
                # Look through all word-lists
                lWords = oData['words']
                for oThis in lWords:
                    sType = oThis['type']
                    for sWord in oThis['form']:
                        oWord = {"wtype": sType,
                                 "wform": sWord}
                        self.loc_words.append(oWord)
                    # Check if this type is already in our list
                    if not sType in self.loc_types:
                        self.loc_types.append(sType)
                # Return okay
                return True
            # Getting here means something went wrong
            return False
        except:
            # act upon error
            self.errHandle.DoError("advHandle/load")
            return False

    def getType(self, sWrd):
        """get the adverb type for this word"""
        sWrd = sWrd.lower()
        for w in self.loc_words:
            if w['wform'] == sWrd:
                return w['wtype']
        # Otherwise return empty
        return ""

    def getTypeCountObject(self, sMethod):
        """Create a new object to count the types defined in [loc_words]"""

        oNew = {}
        for w in self.loc_words:
            if sMethod == "full":
                sWord = w['wform']
                oNew[sWord] = 0
            elif sMethod == "compact":
                wtype = w['wtype']
                if wtype not in oNew:
                    oNew[wtype] = 0

        # Return the result
        return oNew

    def addTypes(self, lstThis, sMethod):
        """Add the types we have to the list [lstThis]"""

        try:
            # Action depends on the method
            if sMethod == "full":
                for w in self.loc_words:
                    lstThis.append(w['wtype'] + "." + w['wform'])
            elif sMethod == "compact":
                for sType in self.loc_types:
                    lstThis.append(sType)
            # Return the result
            return lstThis
        except:
            # act upon error
            self.errHandle.DoError("advHandle/addTypes")
            return None
                