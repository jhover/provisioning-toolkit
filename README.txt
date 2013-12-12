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
 

 
Embed file contents into partial TDL 
 
embed-files -o work/sl6-x86_64-base.files.tdl --fileroot provisioning-templates/files provisioning-templates/sl6-x86_64-base.files.yaml

Merge file TDL with general TDL

merge-tdls -o work/sl6-x86_64-base-withfiles.tdl work/sl6-x86_64-base.files.tdl provisioning-templates/sl6-x86_64-base.tdl



Create image in Openstack.  
 
glance image-create --id ifsl64one --name ifsl64one --disk-format qcow2 --container-format bare --file /home/imagefactory/lib/storage/45e7664b-0486-4569-a915-1bf2583094e3.body --is-public False

glance image-create --name ifsl64one --disk-format qcow2 --container-format bare --file /home/imagefactory/lib/storage/45e7664b-0486-4569-a915-1bf2583094e3.body --is-public False
 