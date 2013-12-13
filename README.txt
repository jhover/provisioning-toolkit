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

  
TEMPLATE CREATION

-- File content cannot contain a few characters which are special to XML. You must replace '<' with &lt;   and &   with &amp;

-- 



VM CREATION

profile 1    +    profile 2   +   profile 3
 files+TDL         files+TDL       files+TDL
 

 
Embed file contents into partial TDL 
 
embed-files -o work/sl6-x86_64-base.files.tdl --fileroot provisioning-templates/files provisioning-templates/sl6-x86_64-base.files.yaml

Merge file TDL with general TDL

merge-tdls -o work/sl6-x86_64-base-withfiles.tdl work/sl6-x86_64-base.files.tdl provisioning-templates/sl6-x86_64-base.tdl

Build base image:

imagefactory --verbose base_image work/sl6-x86_64-base-withfiles.tdl

Note imageID:  e.g. c9d8b606-2776-439a-b206-1a66c0b8b1a6

imagefactory --verbose target_image  --id c9d8b606-2776-439a-b206-1a66c0b8b1a6 openstack-kvm

Note target image id:  e.g. ba7fa96d-e892-4471-a1da-a1990104ffcc

imagefactory --verbose target_image  -id c9d8b606-2776-439a-b206-1a66c0b8b1a6 ec2

Note target image id:

fef23f6f-20c9-401a-852f-20a179b97ab0






Create image in Openstack:
 
glance image-create --id ifsl64one --name ifsl64one --disk-format qcow2 --container-format bare --file /home/imagefactory/lib/storage/45e7664b-0486-4569-a915-1bf2583094e3.body --is-public False

glance image-create --name ifsl64one --disk-format qcow2 --container-format bare --file /home/imagefactory/lib/storage/45e7664b-0486-4569-a915-1bf2583094e3.body --is-public False
 