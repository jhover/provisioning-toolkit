Provisioning Toolkit
=====================

This overall project is intended to bring together a general-purpose set of utilities and practices for creating and managing customized virtual machine resources. The components of the project are:

provisioning-toolkit
--------------------
   -- I.e. hierarchical 'make' using imagefactory.
   -- Scripts to embed file contents into TDLs (embed-files)
   -- Scripts to merge TDLs hierarchically (restoring Boxgrinder's ability to have an inheritance tree of image definitions). (merge-tdls)
   -- Script to invoke iagefactory/oz to build images (imgfac-build)
   -- Imagefactory, euca-tools, or glance to upload/register images.

provisioning-templates
----------------------
 -- TDL (template descripion language) files for use with imagefactory. 
 -- Feature-specific files processed 

provisioning-config
-------------------
  -- RPM to be installed on VMs for profile-specific build and runtime configuration. 
  -- Uses puppet apply 
  -- Base and customized configuration embodied in Hiera .yaml files. Defaults included at build-time. Additional local customization (e.g. via userdata) at runtime.
  -- Includes parameterized Puppet modules for all config tasks, e.g.
    -- ssh authorized keys setup
    -- ephemeral disk detection and setup
    -- condor daemon (startd, schedd, central manager) configuration
    -- cvmfs setup and config
    -- osg worker node config
    -- atlas worker node config

RATIONALES
-- A desire to use as much standard off-the-shelf (preferably non-cloud) software as possible. Thus imagefactory, Puppet/Hiera, and Yum/RPM as core technologies. 

-- We must use *masterless* Puppet to avoid scaling issues and the problem of certificate generation and validation in a dynamic context. Unfortunately this limits the existing/3rd party puppet modules we can use, but the benefits outweigh that. 

-- I want to be able to use the same configuration approach in Clouds and non-Cloud settings. (I want as little custom work as possible when in a cloud environment.) In theory, the node configuration component of this project could be used to manage bare-metal hosts. 

-- Because Puppet modules are installed locally via RPM, you get config versioning for free.
   -- See http://www.slideshare.net/PuppetLabs/bashton-masterless-puppet
   -- We are already experienced in building RPMs and maintaining Yum repos, so this was no extra trouble. 

-- We want to have flexibility between: 
  1) "Baking in" most or all of the node configuration at VM build time, or 
  2) Customizing all config at VM runtime, 
  3) Any balance between the two,

ALTERNATIVES

Cloud-init


Heppix contextualization 









 