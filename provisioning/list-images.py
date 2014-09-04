#!/bin/env python
#
# lists all images in various build states in /var/lib/imagefactory/storage
#

imagedir = "/var/lib/imagefactory/storage"

#
#

import glob
import json
from os import path
from pprint import pprint
import time
import datetime
from xml.etree import ElementTree


#json_file='a.json' 
filelist = glob.glob("%s/*.meta" % imagedir)

for f in filelist:
    
    
    json_data=open(f)
    t = path.getmtime(f)
    ftime = datetime.datetime.fromtimestamp(t)
    data = json.load(json_data)
    json_data.close()
    #pprint(data)
    s = "Image: "
    s += " %s " % ftime
    s+= " %s " % data['identifier']
    s+= " %s " % data['type']
 
    template = data['template']
    tree = ElementTree.fromstring(template)
    root = tree.getroot()
    for child in root:
        s += " %s:%s " %(child.tag, child.attrib)
        
    print(s)



