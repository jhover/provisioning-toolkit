Provisioning Toolkit
=====================

This project is intended to bring together a general-purpose set of utilities and practices for creating and managing virtual machines resources. 

OVERVIEW

-- Scripts to embed file contents into TDLs

-- Scripts to merge TDLs hierarchically (restoring the ability a la Boxgrinder to have an inheritance tree of image definitions). 

-- Imagefactory/oz to build images

-- Imagefactory, euca-tools, or glance to upload/register images. 

-- CloudInit to handle early runtime contextualization
  -- e.g. mounting ephemeral storage.

-- Puppet to handle build-time customization. 

-- Puppet to handle run-time configuration adjustment. 

  
  
VM CREATION

profile 1    +    profile 2   +   profile 3
 files+TDL         files+TDL       files+TDL
 
