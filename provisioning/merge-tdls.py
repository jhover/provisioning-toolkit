#!/bin/env python
# 
# Program to merge imagefactory TDL (Template Description Language) XML files to allow
# an inheritance tree. 
# TDLs specified later on the command line with identical elements override TDLs earlier. 
# Otherwise, content is merged. 
#
from xml.etree import ElementTree

import sys
import logging



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
    tree = None
    for filename in files:
        print("Processing file %s" % filename)
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
        print("Tags not equivalent! Problem! %s != %s" % (first.tag, second.tag))
    else:
        print("Tags equal: %s == %s" % (first.tag, second.tag))
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
            print("Adding missing child %s to first"% secondchild)
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
    #elif a.tail < b.tail:
    #    return -1
    #elif a.tail > b.tail:
    #    return 1

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



def sortattrib(attribhash):
    pass

  
    
def handlefiles(files):
    for filename in files:
        print("Processing file %s ***********************************" % filename)
        root = ElementTree.parse(filename).getroot() 
        printelements(root)
    print("Merging files ***********************************" % files)
    merged = mergefiles(files)
    print("Printing merged structure ***********************************")
    printelements(merged.getroot())
    print(merged)
    merged.write(sys.stdout)
        
def printelements(elem, depth=0):
    indent = "   " * depth
    if elem.text != None and elem.text.strip() != '':
        print("%s %s %s: '%s'" % (indent, elem.tag, elem.attrib, elem.text.strip()))
    else:
        print("%s %s %s" % (indent, elem.tag, elem.attrib))
    for child in elem:
        printelements(child, depth + 1)


def main():
    print(sys.argv)
    files = sys.argv[1:]
    print(files)
    handlefiles(files)
   


if __name__ == "__main__":
    main()