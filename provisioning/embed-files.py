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
import os

def handlefiles(files, outfile= sys.stdout , fileroot = None ):   
    if outfile != sys.stdout:
        of = open(outfile, 'w')
    else:
        of = sys.stdout
    
    of.write("<template>\n   <files>\n")
    for file in files:
        with open(file, 'r') as f:
            doc = yaml.load(f)
            filepairs = doc['files']                
            for targetfile in filepairs.keys():
                sourcefile = filepairs[targetfile]
                if fileroot:
                    sourcefile = "%s/%s" % (fileroot, sourcefile)
                    log.debug("sourcefile path is %s" % sourcefile)
                filecontent = open(sourcefile).read()
                of.write("         <file name=%s>%s</file>\n" % (targetfile,filecontent)) 
    of.write("  </files>\n</template>")
    of.close()

def ensurefile(filepath, clear = False):
    filepath = os.path.expandvars(filepath)
    filepath = os.path.expanduser(filepath)
    d = os.path.dirname(filepath)
    if not os.path.exists(d):
        os.makedirs(d)
    if not os.path.exists(filepath):
        open(filepath, 'w').close()
    elif clear:
        open(filepath, 'w').close()



def main():
      
    global log
            
    debug = 0
    info = 0
    warn = 0
    logfile = sys.stderr
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
        -L --logfile                STDERR
     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvL:r:o:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "logfile=",
                                    "fileroot=",
                                    "outfile=",
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
        elif opt in ("-r", "--fileroot"):
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
    if logfile != sys.stderr:
        ensurefile(logfile)        
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
    files = args
    log.debug(files)
    log.info("Handling files with Logfile=%s Outfile=%s and Fileroot=%s" % (logfile, outfile, fileroot))    
    
    if files:
        if outfile != sys.stderr:
            ensurefile(outfile, clear=True)
        handlefiles(files, outfile, fileroot )


if __name__ == "__main__":
    main()