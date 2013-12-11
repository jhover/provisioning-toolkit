#!/bin/env python
# 
# Takes in .yaml template files and embeds content of files into TDL-compilant XML files. 
#   
#  files:
#     "/path/to/file/filename1.txt" : "local/relative/path/file.txt"
#     "/path/to/file/filename2.txt" : "local/relative/path/file2.txt"
# 
#  PRODUCES --->
#
#  <template>
#    <files>
#      <file name='/path/to/file/filename1.txt'>Content of file 1</file>
#      <file name='/path/to/file/filename2.txt'>Content of file 2</file>
#    </files>
#  <template>
from __future__ import print_function
import sys
import yaml
import getopt
import logging

def handlefiles(files, fileroot = None ):
    print("<template>\n   <files>")
    for file in files:
        with open(file, 'r') as f:
            doc = yaml.load(f)
            print(doc, file=sys.stderr)
            filepairs = doc['files']                
            for targetfile in filepairs.keys():
                sourcefile = filepairs[targetfile]
                if not fileroot:
                    filecontent = open(sourcefile).read()
                print("         <file name=%s>%s</file>" % (targetfile,filecontent)) 
    print("  </files>\n</template>")

def main():
      
    global log
    global outfile
        
    debug = 0
    info = 1
    warn = 0
    logfile = None
    outfile = sys.stdout
    fileroot = None
    
    usage = """Usage: embed.py [OPTIONS] FILE1  [ FILE2  FILE3 ] 
   embed-files takes one or more YAML file specifications and merges them, 
   creating a TDL-compatible template file with the file contents embeded.  
   OPTIONS: 
        -h --help                   Print this message
        -d --debug                  Debug messages
        -V --version                Print program version and exit.
        -r --fileroot               <working directory>
        -o --outfile                STDOUT
     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvr:o:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "fileroot",
                                    "outfile",
                                    ])
    except getopt.GetoptError, error:
        print( str(error))
        print( usage )                          
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)                     
            sys.exit()            
        elif opt in ("-d", "--debug"):
            debug = 1
        elif opt in ("-v", "--verbose"):
            info = 1
        elif opt in ("-L","--logfile"):
            logfile = arg
        elif opt in ("-o","--outfile"):
            outfile = arg
        elif opt in ("-r", --"fileroot"):
            fileroot = arg
    
    major, minor, release, st, num = sys.version_info
    FORMAT24="[ %(levelname)s ] %(asctime)s %(filename)s (Line %(lineno)d): %(message)s"
    FORMAT25="[%(levelname)s] %(asctime)s %(module)s.%(funcName)s(): %(message)s"
    FORMAT26=FORMAT25
    FORMAT27=FORMAT26
    
    if major == 2:
        if minor == 4:
            formatstr = FORMAT24
        elif minor == 5:
            formatstr = FORMAT25
        elif minor == 6:
            formatstr = FORMAT26
        elif minor == 7:
            formatstr = FORMAT27
            
    log = logging.getLogger()
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(formatstr)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    # Handle file-based logging.
    if logfile:
        hdlr = logging.FileHandler(logfile)
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)

    if warn:
        log.setLevel(logging.WARN)
    if debug: 
        log.setLevel(logging.DEBUG) # Override with command line switches
    if info:
        log.setLevel(logging.INFO) # Override with command line switches

    log.debug("%s" %sys.argv)
    files = sys.argv[1:]
    log.debug(files)
    handlefiles(files)


if __name__ == "__main__":
    main()