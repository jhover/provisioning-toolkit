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

#
#     Classes
#
class MergeTDLs(object):

    def __init__(self, files, outfile=sys.stdout):
        self.log = logging.getLogger()
        self.files = files
        self.outfile = outfile

    def handlefiles(self):
        if self.outfile != sys.stdout:
                ensurefile(self.outfile, clear=True)
        for filename in self.files:
            self.log.debug("Processing file %s *******************" % filename)
            root = ElementTree.parse(filename).getroot() 
            self.printelements(root)
        self.log.debug("Merging files *******************" % self.files)
        merged = self.mergefiles()
        self.log.debug("Printing merged structure *******************")
        #self.log.debug(merged)        
        if self.log.isEnabledFor(logging.DEBUG):
            s = self.printelements(merged.getroot())
            self.log.debug(s)
        if self.outfile != sys.stdout:
            self.outfile = open(outfile, 'w')
        merged.write(self.outfile)
        if self.outfile != sys.stdout:
            self.outfile.close()

    def mergefiles(self):
        first = None
        tree = None
        for filename in self.files:
            self.log.debug("Processing file %s" % filename)
            if first is None:
                tree = ElementTree.parse(filename)
                root = tree.getroot()
                first = root
            else:
                second = ElementTree.parse(filename).getroot()
                self.mergetree(first, second)
        return tree
    
    def mergetree(self, first, second):
        if first.tag != second.tag:
            self.log.debug("Tags not equivalent! Problem! %s != %s" % (first.tag, second.tag))
        else:
            self.log.debug("Tags equal: %s == %s" % (first.tag, second.tag))
            if first.text != second.text:
                # Handle template name via concatenation, not replacement, whenever the 
                # string is different. 
                if first.tag.strip() == "name":
                    self.log.debug("Found different 'name' tag. Concatenating.")
                    first.text = "%s-%s" % (first.text, second.text)
                else:
                    first.text = second.text
    
        firsttags = []
        # Look for second children that have same tag, but no attributes, 
        # and merge them.
        for firstchild in first:
            firsttags.append(firstchild.tag)
            for secondchild in second:
                if secondchild.tag == firstchild.tag:
                    if not firstchild.attrib and not secondchild.attrib:
                        # for attribute-less elements, we can simple descend
                        self.mergetree(firstchild, secondchild)
    
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
                    if self.eq_elements(firstchild, secondchild):
                        found = True
                        toremove.append(firstchild)
            
        for el in toremove:
            first.remove(el)
        for el in toadd:
            first.append(el)
           
        # add completely missing children   
        for secondchild in second:
            if secondchild.tag not in firsttags:
                self.log.debug("Adding missing child %s to first"% secondchild)
                first.append(secondchild)
    
    def eq_elements(self, first, second):     
        ret = False
        if self.cmp_elements(first,second) == 0:
            ret = True
        return ret
            
    
    def cmp_elements(self, a,b):
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
        achildren.sort(cmp=self.cmp_elements)
        bchildren = list(b)
        bchildren.sort(cmp=self.cmp_elements)
    
        for achild, bchild in zip(achildren, bchildren):
            cmpval = self.cmp_elements(achild, bchild)
            if  cmpval < 0:
                return -1
            elif cmpval > 0:
                return 1    
        #must be equal 
        return 0
    
    def printelements(self, elem, depth=0):
        indent = "   " * depth
        s = ""
        if elem.text != None and elem.text.strip() != '':
            s += "%s %s %s: '%s'" % (indent, elem.tag, elem.attrib, elem.text.strip())
            #self.log.debug("%s %s %s: '%s'" % (indent, elem.tag, elem.attrib, elem.text.strip()))
        else:
            s += "%s %s %s" % (indent, elem.tag, elem.attrib)
            #self.log.debug("%s %s %s" % (indent, elem.tag, elem.attrib))
        for child in elem:
            s += self.printelements(child, depth + 1)
        return s


class MergeTDLsCLI(object):
    '''
    Utility class to handle command line processing...
    
    '''
    def __init__(self):
        self.debug = 0
        self.info = 0
        self.warn = 0
        self.logfile = sys.stderr
        self.outfile = sys.stdout
        
        self.usage = """Usage: merge-tdls.py [OPTIONS] FILE1  FILE2 [ FILE3 ] 
       merge-tdls takes multiple TDLs and merges them, with later TDLs overriding earlier ones. 
       OPTIONS: 
            -h --help                   Print this message
            -d --debug                  Debug messages
            -v --verbose                Verbose messages
            -L --logfile                STDERR
            -V --version                Print program version and exit.
            -o --outfile                STDOUT
            
         """

    def execute(self):
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
            print( self.usage )                          
            sys.exit(1)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print(self.usage)                     
                sys.exit()            
            elif opt in ("-d", "--debug"):
                self.debug = 1
            elif opt in ("-v", "--verbose"):
                self.info = 1
            elif opt in ("-L","--logfile"):
                self.logfile = arg
            elif opt in ("-o","--outfile"):
                self.outfile = arg
        
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
                
        self.log = logging.getLogger()
        hdlr = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(formatstr)
        hdlr.setFormatter(formatter)
        self.log.addHandler(hdlr)
        # Handle file-based logging.
        if self.logfile != sys.stderr:
            ensurefile(self.logfile)        
            hdlr = logging.FileHandler(logfile)
            hdlr.setFormatter(formatter)
            self.log.addHandler(hdlr)
    
        if self.warn:
            self.log.setLevel(logging.WARN)
        if self.debug: 
            self.log.setLevel(logging.DEBUG) # Override with command line switches
        if self.info:
            self.log.setLevel(logging.INFO) # Override with command line switches
        
        self.log.debug("%s" %sys.argv)
        files = args
        self.log.debug(files)
    
        if files:
            self.mt = MergeTDLs(files)
            self.mt.handlefiles()
#
#    Functions
#
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

#
#   Handle direct running
#
if __name__ == "__main__": 
    cli = MergeTDLsCLI()
    cli.execute()