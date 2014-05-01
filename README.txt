Provisioning Toolkit
=====================

This project is intended to bring together a general-purpose set of utilities and practices for creating and managing virtual machines resources. 

OVERVIEW

-- Scripts to embed file contents into TDLs

-- Scripts to merge TDLs hierarchically (restoring the ability a la Boxgrinder to have an inheritance tree of image definitions). 

-- Imagefactory/oz to build images

-- Imagefactory, euca-tools, or glance to upload/register images. 

-- Base and customized configuration embodied in Hiera .yaml files. Defaults included at build-time. Additional local customization (e.g. via userdata) at runtime. 

-- Puppet to handle build-time customization. 

-- Puppet to handle run-time configuration adjustment.

RATIONALES
-- I want to use as much standard off-the-shelf (even non-cloud) software as possible. Thus imagefactory and Puppet/Hiera, and Condor as core technologies. 

-- I want to use *masterless* Puppet to avoid scaling issues and the problem of certificate generation and validation. This limits the existing/3rd party puppet modules we can use, but the benefits outweigh that. 

-- I want to be able to use the same configuration approach in clouds and non-cloud settings. (I want as little custom work as possible when in a cloud environment.)

-- Because Puppet modules are installed locally via RPM, you get config versioning.
   -- See http://www.slideshare.net/PuppetLabs/bashton-masterless-puppet

-- I want to have flexibility between: 
  1) "Baking in" most or all of the node configuration at VM build time, or 
  2) Customizing all config at VM runtime, or
  3) Any balance between the two. 




  
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

0144e595-13cb-40e1-b759-f631edc06c16


Create and upload image in Openstack:
. nova-essex/novarc

 glance image-create --name sl6-x8664-if-base --disk-format raw --container-format bare --file /home/imagefactory/lib/storage/0144e595-13cb-40e1-b759-f631edc06c16.body --is-public False

'glance image-list' to check

'euca-describe-images' to get ami ID. 

'euca-run-instance <ami-id>' to run. 



 