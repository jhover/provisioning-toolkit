#!/bin/env python
#

#import xml.dom.minidom
from xml.etree import ElementTree

import sys

def __parseopts(self):
    parser = OptionParser(usage='''%prog [OPTIONS]
merge-tdls takes multiple TDLs and merges them, with later TDLs overriding earlier ones. 
This program is licenced under the GPL, as set out in LICENSE file.
Author(s):
John Hover <jhover@bnl.gov>
''', version="1.0")
    parser.add_option("--files", dest="files", 
                          action="store", 
                          metavar="FILES", 
                          help="Files to merge.")
    options, args = parser.parse_args()



def mergefiles(files):
    first = None
    for filename in files:
        data = ElementTree.parse(filename).getroot()
        if first is None:
            first = data
        else:
            first.extend(data)
    if first is not None:
        print ElementTree.tostring(first)


def main():
    print(sys.argv)
    files = sys.argv[1:]
    print(files)
    mergefiles(files)
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