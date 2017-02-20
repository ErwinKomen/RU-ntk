# ==========================================================================================================
# Name :    kamer
# Goal :    Extract intensifiers from political debate texts
# History:
# 16/feb/2017    ERK Created
# ==========================================================================================================
import sys, getopt, os.path, importlib
import util, advhandle, ntk, csv, io

# ============================= LOCAL VARIABLES ====================================
errHandle = util.ErrHandle()
outputColumns = ['Jaar_start', 'Jaar_eind', 'Partij', 'Aanspreek', 'Sentence']

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
  sMethod = 'compact' # Output method: "compact", "full"
  sScope = 'line'     # Scope of the input: "line", "sentence"

  try:
    # Adapt the program name to exclude the directory
    index = prgName.rfind("\\")
    if (index > 0) :
      prgName = prgName[index+1:]
    sSyntax = prgName + ' [-m <method>] [-s <scope>] -a <adverb file> -i <input directory> -o <output directory>'
    # get all the arguments
    try:
      # Get arguments and options
      opts, args = getopt.getopt(argv, "hs:m:a:i:o:", ["-method=","-adverbs=","-inputdir=","-outputdir="])
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
      elif opt in ("-m", "--method"):
        sMethod = arg
      elif opt in ("-s", "--scope"):
        sScope = arg
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
    errHandle.Status('Reading scope is "' + sScope + '"')
    errHandle.Status('Output method is "' + sMethod + '"')
    # Call the function that does the job
    oArgs = {'input': flInput,
             'output': flOutput,
             'adverb': flAdverb,
             'scope': sScope,
             'method': sMethod}
    if (intensifiers(oArgs)) :
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
def intensifiers(oArgs):
    oAdv = None     # 
    bDoAsk = False  # Local variable
    flInput = ""    # 
    flOutput = ""   # 
    flAdverb = ""   # 
    sMethod = ""    # 
    sScope = ""
    arInput = []    # Array of input files
    arOutput = []   # Array of output files
    lOutput = []    # List of output objects (one per hit)

    try:
        # Recover the arguments
        if "input" in oArgs: flInput = oArgs["input"]
        if "output" in oArgs: flOutput = oArgs["output"]
        if "adverb" in oArgs: flAdverb = oArgs["adverb"]
        if "method" in oArgs: sMethod = oArgs["method"]
        if "scope" in oArgs: sScope = oArgs["scope"]
        # Check input and output directories
        if not os.path.isdir(flInput):
            errHandle.Status("Please specify an input DIRECTORY")
            return False
        # Double check the output
        if os.path.exists(flOutput):
            # Check if it accidentily is a directory
            if os.path.isdir(flOutput):
                errHandle.Status("Please specify an output FILE")
                return False
            else:
                # give warning that we will overwrite
                errHandle.Status("We will overwrite existing output file")
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

        # start a CSV writer
        fl_out = io.open(flOutput, "w", encoding='utf-8', newline ='')
        writer = csv.writer(fl_out, csv.excel_tab, lineterminator='\n')
        # BOM to indicate that this is UTF8
        # fl_out.write(u'\ufeff'.encode('utf8'))
        # Create the first row with the headings
        fields = oAdv.addTypes(outputColumns, sMethod)
        writer.writerow(fields)
        # Handle all the files in the input
        for index in range(len(arInput)):
            # Show which file we are treating
            errHandle.Status("Processing file: " + arInput[index])
            # Transform this XML file into an object
            tree = oNtk.load(arInput[index])
            # Evaluate the intensifiers in this file
            lUtt = oNtk.getUtteranceList(tree, arInput[index], oAdv, sMethod)
            # Add the intensifiers to the CSV we are creating
            for utt in lUtt:
                content = []
                # Append the standard lines
                content.append(utt['jaar_van'])
                content.append(utt['jaar_tot'])
                content.append(utt['partij'])
                content.append(utt['aanspr'])
                content.append(utt['s'])
                # Append the count lines
                oCount = utt['count']
                for cnt in oCount:
                    content.append(oCount[cnt])
                # Add line to CSV
                writer.writerow(content)

        # Wrap up the CSV
        fl_out.close()

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