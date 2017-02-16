# ==========================================================================================================
# Name :    kamer
# Goal :    Extract intensifiers from political debate texts
# History:
# 16/feb/2017    ERK Created
# ==========================================================================================================
import sys, getopt, os.path, importlib
import util, advhandle, ntk

# ============================= LOCAL VARIABLES ====================================
errHandle = util.ErrHandle()

# ----------------------------------------------------------------------------------
# Name :    main
# Goal :    Main body of the function
# History:
# 4/apr/2016    ERK Created
# ----------------------------------------------------------------------------------
def main(prgName, argv) :
  flInput = ''        # input directory name
  flOutput = ''       # output directory name
  flAdverb = ''       # intensifier adverb JSON file

  try:
    # Adapt the program name to exclude the directory
    index = prgName.rfind("\\")
    if (index > 0) :
      prgName = prgName[index+1:]
    sSyntax = prgName + ' [-a <adverb file>] -i <input directory> -o <output directory>'
    # get all the arguments
    try:
      # Get arguments and options
      opts, args = getopt.getopt(argv, "ha:i:o:", ["-adverbs=","-inputdir=","-outputdir="])
    except getopt.GetoptError:
      print(sSyntax)
      sys.exit(2)
    # Walk all the arguments
    for opt, arg in opts:
      if opt == '-h':
        print(sSyntax)
        sys.exit(0)
      elif opt in ("-a", "--adverbs"):
        flAdverb = arg
      elif opt in ("-i", "--ifile"):
        flInput = arg
      elif opt in ("-o", "--ofile"):
        flOutput = arg
    # Check if all arguments are there
    if (flInput == '' or flOutput == ''):
      errHandle.DoError(sSyntax)
    # Continue with the program
    errHandle.Status('Input is "' + flInput + '"')
    errHandle.Status('Output is "' + flOutput + '"')
    errHandle.Status('Adverb definition file is "' + flAdverb + '"')
    # Call the function that does the job
    if (intensifiers(flInput, flOutput, flAdverb)) :
      errHandle.Status("Ready")
    else :
      errHandle.DoError("Could not complete")
  except:
    # act
    errHandle.DoError("main")
    return False

# ----------------------------------------------------------------------------------
# Name :    intensifiers
# Goal :    Find intensifiers in the input files
# History:
# 16/feb/2017    ERK Created
# ----------------------------------------------------------------------------------
def intensifiers(flInput, flOutput, flAdverb):
    oAdv = None
    bDoAsk = False                  # Local variable
    arInput = []                    # Array of input files
    arOutput = []                   # Array of output files
    lOutput = []                    # List of output objects (one per hit)

    try:
        # Check input and output directories
        if not os.path.isdir(flInput):
            errHandle.Status("Please specify an input directory")
            return False
        if not os.path.isdir(flOutput):
            errHandle.Status("Please specify an output directory")
            return False
        # Read input files
        for flThis in os.listdir(flInput):
            # Only take the XML files in the directory
            if flThis.endswith(".xml"):
                # Add file to list
                arInput.append(os.path.normpath(flInput + "/" + flThis))

        # Read the adverbs
        oAdv = advhandle.AdvHandle(errHandle)
        oAdv.Load(flAdverb)

        # Make a file handler
        oNtk = ntk.ntk(errHandle)

        # Handle all the files in the input
        for index in range(len(arInput)):
            # Transform this XML file into an object
            tree = oNtk.load(arInput[index])
            # Process this one file
            lUtt = oNtk.getUtteranceList(tree, oAdv)

        # We are happy: return okay
        return True
    except:
        # act
        errHandle.DoError("intensifiers")
        return False



# ----------------------------------------------------------------------------------
# Goal :  If user calls this as main, then follow up on it
# ----------------------------------------------------------------------------------
if __name__ == "__main__":
  # Call the main function with two arguments: program name + remainder
  main(sys.argv[0], sys.argv[1:])