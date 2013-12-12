#!/bin/env python
# 
# Program to merge imagefactory TDL (Template Description Language) XML files to allow
# an inheritance tree. 
# TDLs specified later on the command line with identical elements override TDLs earlier. 
# Otherwise, content is merged. 
#
from xml.etree import ElementTree

import getopt
import logging
import os
import sys

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
            

def mergefiles(files):
    first = None
    tree = None
    for filename in files:
        log.debug("Processing file %s" % filename)
        if first is None:
            tree = ElementTree.parse(filename)
            root = tree.getroot()
            first = root
        else:
            root = ElementTree.parse(filename).getroot()
            mergetree(tree.getroot(), root)
    return tree

def mergetree(first, second):
    if first.tag != second.tag:
        log.debug("Tags not equivalent! Problem! %s != %s" % (first.tag, second.tag))
    else:
        log.debug("Tags equal: %s == %s" % (first.tag, second.tag))
        if first.text != second.text:
            first.text = second.text


    firsttags = []
    # Handle look for second children that have same tag, but no attributes, 
    # and merge them.
    #
    for firstchild in first:
        firsttags.append(firstchild.tag)
        for secondchild in second:
            if secondchild.tag == firstchild.tag:
                if not firstchild.attrib and not secondchild.attrib:
                    # for attribute-less elements, we can simple descend
                    mergetree(firstchild, secondchild)

    # For elements with same tags, but having attributes, we need to 
    # handle them more carefully,since there may be multiple children with the same tag 
    # e.g. 'package' but different attributes, e.g. 'name' = 'yum' 
    toremove = []
    toadd = []
    
    for secondchild in second:
        if secondchild.attrib:
            found = False
            toadd.append(secondchild)
            for firstchild in first:
                if eq_elements(firstchild, secondchild):
                    found = True
                    toremove.append(firstchild)
        
    for el in toremove:
        first.remove(el)
    for el in toadd:
        first.append(el)
       
    # add completely missing children   
    for secondchild in second:
        if secondchild.tag not in firsttags:
            log.debug("Adding missing child %s to first"% secondchild)
            first.append(secondchild)
    


def eq_elements(first, second):
    
    ret = False
    if cmp_elements(first,second) == 0:
        ret = True
    return ret
        

def cmp_elements(a,b):
    '''
    Taken from http://stackoverflow.com/questions/7905380/testing-equivalence-of-xml-etree-elementtree
    '''
    
    if a.tag < b.tag:
        return -1
    elif a.tag > b.tag:
        return 1

    #compare attributes
    aitems = a.attrib.items()
    aitems.sort()
    bitems = b.attrib.items()
    bitems.sort()
    if aitems < bitems:
        return -1
    elif aitems > bitems:
        return 1

    #compare child nodes
    achildren = list(a)
    achildren.sort(cmp=cmp_elements)
    bchildren = list(b)
    bchildren.sort(cmp=cmp_elements)

    for achild, bchild in zip(achildren, bchildren):
        cmpval = cmp_elements(achild, bchild)
        if  cmpval < 0:
            return -1
        elif cmpval > 0:
            return 1    
    #must be equal 
    return 0

    
def printelements(elem, depth=0):
    indent = "   " * depth
    if elem.text != None and elem.text.strip() != '':
        log.debug("%s %s %s: '%s'" % (indent, elem.tag, elem.attrib, elem.text.strip()))
    else:
        log.debug("%s %s %s" % (indent, elem.tag, elem.attrib))
    for child in elem:
        printelements(child, depth + 1)


def handlefiles(files):
    for filename in files:
        log.debug("Processing file %s ***********************************" % filename)
        root = ElementTree.parse(filename).getroot() 
        printelements(root)
    log.debug("Merging files ***********************************" % files)
    merged = mergefiles(files)
    log.debug("Printing merged structure ***********************************")
    printelements(merged.getroot())
    log.debug(merged)
    if outfile != sys.stdout:
        f = open(outfile)
        merged.write(f)
    else:
        merged.write(sys.stdout)


def main():
    
    global log
    global outfile
        
    debug = 0
    info = 0
    warn = 0
    logfile = sys.stderr
    outfile = sys.stdout
    
    usage = """Usage: merge-tdls.py [OPTIONS] FILE1  FILE2 [ FILE3 ] 
   merge-tdls takes multiple TDLs and merges them, with later TDLs overriding earlier ones. 
   OPTIONS: 
        -h --help                   Print this message
        -d --debug                  Debug messages
        -v --verbose                Verbose messages
        -L --logfile                STDERR
        -V --version                Print program version and exit.
        -o --outfile                STDOUT
        
     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvL:o:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "logfile=",
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

    if files:
        if outfile != sys.stdout:
            ensurefile(outfile, clear=True)
        handlefiles(files, outfile, fileroot )

    log.debug(files)
    handlefiles(files)



if __name__ == "__main__": 
    main()