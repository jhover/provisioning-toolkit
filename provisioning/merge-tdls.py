#!/bin/env python
# 
# Program to merge imagefactory TDL (Template Description Language) XML files to allow
# an inheritance tree. 
# TDLs specified later on the command line with identical elements override TDLs earlier. 
# Otherwise, content is merged. 
#
#import xml.dom.minidom
from xml.etree import ElementTree

import sys

def __parseopts(self):
    parser = OptionParser(usage='''%prog [OPTIONS] FILE1 [ FILE2 FILE3 ]
merge-tdls takes multiple TDLs and merges them, with later TDLs overriding earlier ones. 
This program is licenced under the GPL, as set out in LICENSE file.
Author(s):
John Hover <jhover@bnl.gov>
''', version="1.0")
    options, args = parser.parse_args()


def mergefiles(files):
    first = None
    for filename in files:
        print("Processing file %s" % filename)
        root = ElementTree.parse(filename).getroot()
        if first is None:
            first = root
        else:
            first.merge(root)

def mergetree(first, second):
    pass


    
def explorefiles(files):
    for filename in files:
        print("Processing file %s" % filename)
        root = ElementTree.parse(filename).getroot() 
        printelements(root)
        
def printelements(elem, depth=0):
    indent = "  " * depth
    print("%s %s %s" % (indent, elem.tag, elem.attrib))
    for child in elem:
        printelements(child, depth + 1)


def main():
    print(sys.argv)
    files = sys.argv[1:]
    print(files)
    #mergefiles(files)
    explorefiles(files)
    #for f in files:
    #    fh = open(f)
    #    output = fh.read()
    #    print(output)
    #    xmldoc = xml.dom.minidom.parseString(output).documentElement
    #nodelist = []
    #for c in listnodesfromxml(xmldoc, 'c') :
    #    node_dict = node2dict(c)
    #    nodelist.append(node_dict)            
    #log.info('Got list of %d entries.' %len(nodelist))       


if __name__ == "__main__":
    main()