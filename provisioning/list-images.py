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


class ImageInfo(object):
    
    def __init__(self,filetime,identifier,status,name,type, target, provider, provider_identifier):
        self.filetime = filetime
        self.identifier = identifier
        stl = status.lower()
        self.status = stl
        self.name = name
        self.type = type
        self.target = target
        self.provider = provider
        self.pidentifier = provider_identifier
        
        
    def __str__(self):
        s = "Image: "
        s += " %s " % self.filetime
        s+= " %s " % self.identifier
        s+= " %s " % self.status
        
        

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
    st = data['status']
    st = st.lower()
    s+= " %s " % st
    
    template = data['template']
    if template:
        root = ElementTree.fromstring(template)
        for child in root:
            if child.tag == 'name':
                s += " %s " % child.text.strip()
    
    s+= " %s " % data['type']
    t = data['type']
    if t == "TargetImage":
        s+= " %s " % data['target']
    elif t == "ProviderImage":
        s+= " %s " % data['provider']
        s+= " %s " % data['identifier_on_provider']

    print(s)


# status  FAILED
