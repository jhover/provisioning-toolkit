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


def explorefiles(files):
    for file in files:
        with open(file, 'r') as f:
            doc = yaml.load(f)
            print(doc, file=sys.stderr)
            filepairs = doc['files']
            print("<template>\n   <files>")
            
            for targetfile in filepairs.keys():
                sourcefile = filepairs[targetfile]
                filecontent = open(sourcefile).read()
                print("         <file name=%s>%s</file>" % (targetfile,filecontent)) 
            print("  </files>\n</template>")

def main():
    print(sys.argv, file=sys.stderr)
    files = sys.argv[1:]
    print(files, file=sys.stderr)
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