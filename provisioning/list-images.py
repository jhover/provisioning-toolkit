#!/bin/env python
#
# lists all images in various build states in /var/lib/imagefactory/storage
#

imagedir = "/var/lib/imagefactory/storage"

#
#

import glob

import json
import os
from pprint import pprint

#json_file='a.json' 
filelist = glob.glob("%s/*.meta" % imagedir)

for f in filelist:
    json_data=open(f)
    data = json.load(json_data)
    json_data.close()

pprint(data)
# print "Dimension: ", data['cubes'][cube]['dim']



