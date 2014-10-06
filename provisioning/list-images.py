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
    t = data['type']
    if t == "target":
        s+= " %s " % data['target']
    elif t == "provider":
        s+= " %s " % data['provider']
        s+= " %s " % data['identifier_on_provider']
      
        
 
    template = data['template']
    if template:
        root = ElementTree.fromstring(template)
        for child in root:
            if child.tag == 'name':
                s += " %s " % child.text.strip()
    print(s)



