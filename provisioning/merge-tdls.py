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
            mergetree(first,root)
    return first

def mergetree(first, second):
    if first.tag != second.tag:
        print("Tags not equivalent! Problem! %s != %s" % (first.tag, second.tag))
    else:
        print("Tags equal: %s == %s" % (first.tag, second.tag))
    
    firstattribindex = {}
    secondattribindex = {}
    
    firsttags = []
    for firstchild in first:
        firsttags.append(firstchild.tag)
        for secondchild in second:
            if secondchild.tag == firstchild.tag:
                if not firstchild.attrib and not secondchild.attrib:
                    # for attribute-less elements, we can simple descend
                    mergetree(firstchild, secondchild)
                else:
                    # for elements with same tags, but having attibutes, we need to 
                    # handle them more carefully,since there may be multiple children with the same tag 
                    # e.g. 'package' but different attributes, e.g. 'name' = 'yum' 
                    pass        
       
    # add completely missing children   
    for secondchild in second:
        if secondchild.tag not in firsttags:
            first.append(secondchild)
            print("Adding missing child %s to first"% secondchild)


def cmpnodes(first, second):
    # compares tags, attributes, data (.text) 
    # Two nodes are the same if all are the same. 
    #
    print("Comparing nodes %s and %s" % (first,second))
    if first.tag != second.tag:
        print("Tag %s != %s" % (first.tag, second.tag) )
        return cmp(first.tag, second.tag)
    if first.text != second.text:
        print("Text %s != %s" % (first.tag, second.tag) )
        return cmp(first.text,second.text)
    
    fa = first.attrib
    sa = second.attrib
    if cmp(fa,sa) != 0:
        same = False


def sortattrib(attribhash):
    pass

  
    
def explorefiles(files):
    for filename in files:
        print("Processing file %s ***********************************" % filename)
        root = ElementTree.parse(filename).getroot() 
        printelements(root)
    print("Merging files ***********************************" % files)
    merged = mergefiles(files)
    print("Printing merged structure ***********************************")
    printelements(merged)
        
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