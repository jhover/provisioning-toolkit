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

#json_file='a.json' 
filelist = glob.glob("%s/*.meta" % imagedir)

for f in filelist:
    
    
    json_data=open(f)
    ftime = time.ctime(path.getmtime(f))
    
    data = json.load(json_data)
    json_data.close()
    #pprint(data)
    s = "Image: "
    s += " %s " % ftime
    s+= " %s " % data['identifier']
    s+= " %s " % data['type']
   
    template = data['template']
        
    print(s)



