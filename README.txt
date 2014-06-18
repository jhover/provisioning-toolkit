Provisioning Toolkit
=====================

This overall project is intended to bring together a general-purpose set of utilities and practices for creating and managing customized virtual machine resources. The components of the project are:

provisioning-toolkit
--------------------
   -- I.e. hierarchical 'make' using imagefactory.
   -- Scripts to embed file contents into TDLs (embed-files)
   -- Scripts to merge TDLs hierarchically (restoring Boxgrinder's ability to have an inheritance tree of image definitions). (merge-tdls)
   -- Script to invoke imagefactory/oz to build images (imgfac-build)
   -- Imagefactory, euca-tools, or glance to upload/register images.
   -- Tools to generate userdata files and generate HTCondor-G submit files for arbitrary node types. 
     
provisioning-templates
----------------------
 -- TDL (template descripion language) files for use with imagefactory. 
 -- Feature-specific files processed 
 -- Templates for submit-side cloud-init and/or puppet/hiera config generation. 

provisioning-config
-------------------
  -- RPM to be installed on VMs for profile-specific build and runtime configuration. 
  -- Uses 'puppet apply' 
  -- Default and customized configuration embodied in Hiera .yaml files. Defaults included at build-time. Additional local customization (e.g. via userdata) at runtime.
  -- Includes parameterized Puppet modules for all config tasks, e.g.
    -- ssh authorized keys setup
    -- ephemeral disk detection and setup
    -- condor daemon (startd, schedd, central manager) configuration
    -- cvmfs setup and config
    -- osg worker node config
    -- atlas worker node config

WORKFLOW SUMMARY

1) Define build template(s)
  -- Include provisioning-config Yum repo and RPM. This RPM contains all Puppet *code* used for config.  
  -- Include any other RPMs desired, so as to minimize runtime RPM downloads
  -- Pre-define Hiera defaults (potentially enough to not require runtime customization at all). 

2) Run imgfac-build to merge and build image for particular platform (EC2, KVM/Openstack, etc).

3) Upload and register image to IaaS. 

4) Invoke image(s) with or without userdata. If userdata is needed, include as a write_files entry creating /etc/hiera/loca.yaml. Add or subtract classes & config to define nodes to different profiles. 

5) cloud-init grabs userdata to disk, creating local.yaml.  

6) Puppet runs via cron at boot and hourly and merges defaults + dynamic config, and applies with puppet. 

The only custom component is the small runpuppet cron script, which runs 'puppet apply'.

Complex virtual layouts (e.g. cluster head node, workers, and squid) will need higher-level orchestration. We are currently looking into an appropriate mechanism for handling this. 
           
           
RATIONALES
-- A desire to use as much standard off-the-shelf (preferably non-cloud) software as possible. Thus imagefactory, Puppet/Hiera, and Yum/RPM as core technologies. 

-- Permit complete configuration at build-time if this is desired. And allow for a continuum of build-time vs. run-time configuration. 

-- We must use *masterless* Puppet to avoid scaling issues and the problem of certificate generation and validation in a dynamic context. Unfortunately this limits the existing/3rd party puppet modules we can use, but the benefits outweigh that. 

-- I want to be able to use the same configuration approach in Clouds and non-Cloud settings. (I want as little custom work as possible when in a cloud environment.) In theory, the node configuration component of this project could be used to manage bare-metal hosts. 

-- Because Puppet modules are installed locally via RPM, you get config versioning for free.
   -- See http://www.slideshare.net/PuppetLabs/bashton-masterless-puppet
   -- We are already experienced in building RPMs and maintaining Yum repos, so this was no extra trouble. 


ALTERNATIVES/ RELATED PROJECTS

HEPPIX contextualization 
------------------------
This is a set of guidelines developed for Cloud VM initialization by a HEPPIX working group. It is based on providing a small ISO9660 disk image to be mounted on the VM, with a defined directory hierarchy, and init scripts which use those settings. 

This was rejected because 1) its very limited user base/audience and thus lack of vigorous maintenance and development, 2) it imposes a set of awkward requirements for use, and 3) only useful in a cloud context.   

Cloud-init
----------
http://cloudinit.readthedocs.org/en/latest/

Cloud-init is a runtime contextualization tool that originated on Debian. It establishes a standard for the userdata format (a mime-multipart file) with a set of supported types, and the init program on the VM to unpack and execute them. It even provides a plugin datasource construct, which can get input data from sources other than the metadata service (e.g. other clouds, mounted config image). 

The only reason this was rejected as a general framework is that it currently doesn't allow usage outside of a cloud context. Also, if one is going to use Puppet, then the cloud-init complex capabilities are overkill. Another negative is that it requires a utility to create the userdata file from sub-components on the submit side, although this is a minor concern.  

As it is, cloud-init could be relatively cleanly integrated with the Puppet infrastructure of this provisioning-X project, by having cloud-init pull the Hiera config from userdata, and execute puppet apply. 

Star Cluster  
------------
http://star.mit.edu/cluster/

Assumes and requires the use of Sun Grid Engine as the local batch system on the virtual cluster. It is still a possibility that this software may be adaptable for use as the orchestration component.  

Henrik's ATLASSGE Modules
-------------------------
https://github.com/spiiph/atlasgce-modules/

These are a set of custom Puppet modules and associated scripts used to bootstrap a virtual cluster on Google Compute Engine. They were not directly usable for this project (e.g., the Puppet modules are not parameterized), but may provide a useful starting point for some node/package types. 


SOURCE CODE
http://svn.usatlas.bnl.gov/svn/griddev/provisioning-toolkit/
http://svn.usatlas.bnl.gov/svn/griddev/provisioning-templates/
http://svn.usatlas.bnl.gov/svn/griddev/provisioning-config/



 