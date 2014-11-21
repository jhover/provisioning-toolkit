#!/bin/env python
#
# Top level Imagefactory build tool
# Usage:
#    imgfac-build  TDL_FILE  [ TDL_FILE ]
#


from __future__ import print_function
import getopt
import logging
import os
import shutil
import StringIO
import sys
import subprocess
import tempfile
import time

from ConfigParser import SafeConfigParser

class ImgfacBuildBaseException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ImgfacBuildTargetException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ImgfacBuildProviderException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class ImgFacBuild(object):
    
    def __init__(self, config, profile):
        self.log = logging.getLogger()
        self.config = config
        self.profile = profile
        self.tdlonly = config.getboolean(profile,'tdlonly')
        self.templates = config.get(profile, 'templates')
        self.templates = self.templates.split(',')
        self.workdir = os.path.expanduser(config.get(profile,'workdir'))
        self.fileroot = os.path.expanduser(config.get(profile,'fileroot'))
        self.target = config.get(profile,'target')
        self.provider = config.get(profile,'provider')    
        self.credentials = os.path.expanduser(config.get(profile, 'credentials'))
      
        # Fix None values.  
        if self.target == 'None': 
            self.target = None
        if self.provider == 'None':
            self.provider = None
        if self.credentials == 'None':
            self.credentials = None        

        self.log.debug("%s" % self)
       
    def __repr__(self):
        s = "ImgFacBuild: "
        s += "fileroot = %s " % self.fileroot
        s += "target = %s " % self.target
        s += "provider = %s " % self.provider
        s += "tdlonly = %s " % self.tdlonly
        s += "workdir = %s " % self.workdir
        s += "templates = %s" % self.templates
        return s

    
        
        
    def build(self):
        self.handle_embedfiles()
        self.make_withfiles()
        self.finaltdl = self.handle_mergetdls()
        self.log.debug("tdlonly value is %s of type %s" % (self.tdlonly, type(self.tdlonly)))
        if self.tdlonly:
            self.log.info("Final TDL produced at: %s" % self.finaltdl)
            self.log.debug("TDL only requested. No build.")
        else:
            self.run_imagefactory()            
          
    def handle_embedfiles(self):
        '''
        Takes a files.yaml file for each name and creates a files.tdl for later merging. 
        '''
        for f in self.templates:
            name = getname(f)
            ext = getext(f)
            p = getpathdir(f)
            self.log.info("Embedding files. Handling %s" % f)
            self.log.debug("Handling path=%s name=%s ext=%s" % (p, name, ext))
            yamlfile = "%s.files.yaml" % name
            self.log.debug("yamlfile=%s" % yamlfile )
            yfp = "%s/%s" % (p, yamlfile)
            self.log.debug("checking if %s exists..." % yfp  ) 
            destname = "%s/%s.files.tdl" % (self.workdir, name)
            if os.path.exists(yfp):
                self.log.debug("yep. running embed_files...")
                cmd = "embed-files -o %s --fileroot %s %s " % ( destname, self.fileroot, yfp)
                self.log.debug("command: %s" % cmd)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                self.log.debug('out = %s' % out)
                self.log.debug('err = %s' % err)
            else:
                self.log.debug("No <name>.files.yaml file so doing nothing.")
    
    def make_withfiles(self):
        '''
        Combine all <name>.files.tdl and <name>.tdl files into <name>.withfiles.tdl
            '''
        for f in self.templates:
            name = getname(f)
            ext = getext(f)
            p = getpathdir(f)
            self.log.info("Handling %s" % f)                  
            self.log.debug("Handling path=%s name=%s ext=%s" % (p, name, ext))
            wfp = "%s/%s.files.tdl" % (self.workdir,name)
            destname = "%s/%s.withfiles.tdl" % (self.workdir,name)
            if os.path.exists(wfp):
                self.log.debug("yep. running merge-tdls...")
                cmd = "merge-tdls -o %s %s %s " % ( destname, f, wfp )
                self.log.debug("command= %s" % cmd)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                self.log.debug('out = %s' % out)
                self.log.debug('err = %s' % err)
            else:
                self.log.debug("No <name>.files.tdl so copying <name>.tdl to <name>.withfiles.tdl...")
                shutil.copy(f, destname)
                self.log.debug("copied %s -> %s" % (f,destname))
    
    
    def handle_mergetdls(self):
        '''
        Combine all <name>.withfiles.tdl into final tdl named
          <name1>-<name2>-<nameN>.tdl
        Return name of final tdl file path. 
        '''
        withfiles = []
        destname = ""
        for f in self.templates:
            name = getname(f)
            ext = getext(f)
            p = getpathdir(f) 
            self.log.info("Handling %s" % f)
            wfp = "%s/%s.withfiles.tdl" % (self.workdir,name)
            withfiles.append(wfp)
            if destname == "":
                destname = "%s" % name
            else:
                destname = "%s-%s" % (destname, name)
        
        self.log.debug("withfiles is %s" % withfiles)
        allfiles = " ".join(withfiles)
        cmd = "merge-tdls -o %s/%s.tdl %s" % (self.workdir, destname, allfiles )
        self.log.debug("command= %s" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        self.log.debug('err = %s' % err)
        self.log.debug('out = %s' % out)
        retval = "%s/%s.tdl" % (self.workdir, destname)
        self.log.debug('returning %s'% retval)
        return retval
    
    
    def run_imagefactory(self):
        self.log.info("Running imagefactory base...")
        try:
            baseuuid = self.run_imagefactory_base(self.finaltdl)
            self.log.info("Ran imagefactory base...") 
            
            if self.target:
                targetuuid = self.run_imagefactory_target(baseuuid)
                self.log.info("Ran imagefactory target: %s" % self.target)
            
            if self.provider:
                self.run_imagefactory_provider(targetuuid)
                self.log.info("Ran imagefactory provider: %s" % self.provider)

        except ImgfacBuildBaseException, e:
            self.log.error("Something went wrong running imagefactory base: %s" % e)
        except ImgfacBuildTargetException, e:
            self.log.error("Something went wrong running imagefactory target: %s" % e)
        except ImgfacBuildProviderException, e:
            self.log.error("Something went wrong running imagefactory provider: %s" % e)
    
    
    def run_imagefactory_base(self, tdlfile):
        '''
    out:    
    ============ Final Image Details ============
    UUID: aee9b860-c067-4ad8-8622-55a785dd96f4
    Type: target_image
    Status: COMPLETE
    Status Details: {'error': None, 'activity': 'Target Image build complete'}
       
        '''
        cmd = "time imagefactory --debug base_image %s " % (tdlfile)
        self.log.info("Running imagefactory: '%s'" % cmd)
        (out, err) = self.run_timed_command(cmd)
        (status, uuid) = self.parse_imagefactory_return(out)
        if status is not True:
            raise ImgfacBuildBaseException("Status was %s, error: %s" % (status, err))
        return uuid        
    
    def run_imagefactory_target(self, uuid):
        '''
        ============ Final Image Details ============
UUID: fb9dad89-b15b-47ad-8d88-76d82f85d8e1
Type: target_image
Image filename: /var/lib/imagefactory/storage/fb9dad89-b15b-47ad-8d88-76d82f85d8e1.body
Image build completed SUCCESSFULLY!

        '''
        

        cmd = "time imagefactory --debug target_image --id %s %s " % (uuid, self.target)
        self.log.info("Running imagefactory: '%s'" % cmd)
        (out, err) = self.run_timed_command(cmd)
        (status, uuid) = self.parse_imagefactory_return(out)
        if status is not True:
            raise ImgfacBuildTargetException("Status was %s, error: %s" % (status, err))
        return uuid

    def run_imagefactory_provider(self, uuid):
        '''
        imagefactory --debug  provider_image --id <id> ec2 @us-east-1 etc/ec2_credentials.xml
        
        ============ Final Image Details ============
UUID: 222505c7-f523-4af9-8770-83ba8dc62b67
Type: provider_image
Image filename: /var/lib/imagefactory/storage/222505c7-f523-4af9-8770-83ba8dc62b67.body
Image ID on provider: ami-7c39a814
Image build completed SUCCESSFULLY!
        
        '''
              
        cmd = "time imagefactory --%s provider_image --id %s %s " % (self.loglevel, 
                                                                     uuid, 
                                                                     self.target, 
                                                                     self.credential)
        self.log.info("Running imagefactory: '%s'" % cmd)
        (out, err) = self.run_timed_command(cmd)
        (status, uuid) = self.parse_imagefactory_return(out)
        
        if status is not True:
            raise ImgfacBuildProviderException("Status was %d, error: %s" % (status, err))
        else:
            self.log.info("Provider image done.")
                   

    def run_timed_command(self, cmd):
        #
        # This is necessary because using subprocess.PIPE and p.communicate() hangs when
        # output is very large. 
        #
        my_stdout = tempfile.NamedTemporaryFile(prefix='imgfac-build-out-', delete=False)        
        my_stderr = tempfile.NamedTemporaryFile(prefix='imgfac-build-err-', delete=False)
        self.log.info("Subcommand output in %s error in %s" % ( my_stdout.name, my_stderr.name))
        self.log.debug("cmd is %s" % cmd)
        p = subprocess.Popen(cmd, stdout=my_stdout, stderr=my_stderr, shell=True)
        self.log.debug("Command running...")
        sec = 0
        retcode = None
        INTERVAL = 30
        while retcode is None:
            retcode = p.poll()
            time.sleep(INTERVAL)
            sec = sec + INTERVAL
            if sec < 60:        
                self.log.debug("%s seconds elapsed..." % sec)
            else:
                min =  sec / 60
                secmod = sec % 60
                self.log.debug("%s min %s sec elapsed..." % (min, secmod))
                if min % 3  == 0 and secmod == 0:
                    self.log.info("Running. %s minutes elapsed..." % min)  
        self.log.info("Command is finished. Processing output...")
        self.log.debug('Rewinding out, err files...')
        my_stdout.seek(0)
        my_stderr.seek(0)
        self.log.debug('Reading out, err into strings...')
        out = my_stdout.read()
        err = my_stdout.read()
        self.log.debug('out = %s' % out)
        self.log.debug('err = %s' % err)
        my_stdout.close()
        my_stderr.close()
        return (out, err)


    def parse_imagefactory_return(self, text):
        uuid = None
        buf = StringIO.StringIO(text)
        for line in buf.readlines():
            #self.log.debug("line is %s" % line)
            h1 = line[:4]
            #print("h1 is '%s'" % h1)
            if h1 == 'UUID':
                #print("h1 does equal 'UUID'")
                uuid = line[6:].strip()
        if uuid is not None:
            self.log.info("Parsed UUID: %s" % uuid)
            return (True, uuid)
        else:
            self.log.error("failed to parse UUID from text: %s" % text)
            return (None, None)


    def parse_imagefactory_return_old(self, text):
        uuid = None
        status = None
        buf = StringIO.StringIO(text)
        for line in buf.readlines():
            #self.log.debug("line is %s" % line)
            h1 = line[:4]
            #print("h1 is '%s'" % h1)
            if h1 == 'UUID':
                #print("h1 does equal 'UUID'")
                uuid = line[6:].strip()
    
            h2 = line[:7]
            #print("h2 is '%s'" % h2)
            if h2 == 'Status:':
                #print("h2 does equal 'Status:'")
                s = line[8:]
                s = s.strip()
                #print("s is '%s'" % s)
                if s == 'COMPLETE':
                    #print("s does equal 'COMPLETE'")
                    status = True
                else:
                    pass
                    #print("%s != %s" % (s,'COMPLETE'))
        if uuid is not None and status is not None:
            self.log.info("Parsed UUID: %s" % uuid)
            return (status, uuid)
        else:
            self.log.error("failed to parse UUID from text: %s" % text)
            return (None, None)
   

def nameext(filename):
    ext = '.'.join(filename.split('.')[-1:])
    name = '.'.join(filename.split('.')[:-1])
    return(name, ext)

def getname(filename):
    fn = os.path.basename(filename)
    name = '.'.join(fn.split('.')[:-1])
    return name

def getext(filename):
    fn = os.path.basename(filename)
    ext = '.'.join(fn.split('.')[-1:])
    return ext

def getpathdir(filename):
    p = os.path.dirname(filename)
    return p

def checkext(filename, ext):
    e = getext(filename)
    if e.lower() != ext.lower():
        raise Exception("All input files must have .%s extension." % ext)



def main():
    
    #global log
    #global workdir
    #global fileroot
    #global target
    #global tdlonly 
    
    debug = False
    info = False
    warn = False
    tdlonly = False
    logfile = sys.stderr
    outfile = sys.stdout
    workdir = os.path.expanduser("~/tmp")
    profile = None
    target = None
    provider = None
    credentials = None
    default_configfile = os.path.expanduser("~/etc/imgfac.conf")
    config_file = None
    
    usage = """Usage: imgfac-build.py [OPTIONS] TDL  [TDL2  FILE3 ] 
   merge-tdls takes multiple TDLs and merges them, with later TDLs overriding earlier ones. 
   OPTIONS: 
        -h --help                   Print this message
        -d --debug                  Debug messages
        -v --verbose                Verbose messages
        -c --config                 Config file [~/.provisioning/imfac.conf]
        -L --logfile                STDERR
        -l --list                   List available builds.
        -r --fileroot               [working directory]
        -V --version                Print program version and exit.
        -o --outfile                STDOUT
        -t --target                 Output format [openstack-kvm|ec2] 
        -w --workdir                Temporary workdir [~/tmp]
        -T --tdlonly                Just create TDL, do not build. 
        -p --profile                Config section to determine action

     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvc:t:r:L:o:w:Tp:P:C:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "config=",
                                    "target=",
                                    "fileroot=",
                                    "logfile=",
                                    "outfile=",
                                    "workdir=",
                                    "tdl",
                                    "profile=",
                                    "provider=",
                                    "credentials=",
                                    ])
    except getopt.GetoptError, error:
        print( str(error))
        print( usage )                          
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage)                     
            sys.exit()            
        elif opt in ("-d", "--debug"):
            debug = True
        elif opt in ("-v", "--verbose"):
            info = True
        elif opt in ("-c", "--config"):
            config_file = arg
        elif opt in ("-t", "--target"):
            target = arg
        elif opt in ("-r","--fileroot"):
            fileroot = arg
        elif opt in ("-L","--logfile"):
            logfile = arg
        elif opt in ("-w", "--workdir"):
            workdir = arg               
        elif opt in ("-T", "--tdl"):
            tdlonly = True
        elif opt in ("-p", "--profile"):
            profile = arg
        elif opt in ("-P", "--provider"):
            provider = arg
        elif opt in ("-C", "--credentials"):
            credentials = arg

    # Read in config file
    #config=SafeConfigParser(allow_no_value=True)
    config=SafeConfigParser()
    if not config_file:
        config_file = default_configfile
    got_config = config.read(config_file)

    
    major, minor, release, st, num = sys.version_info
    FORMAT24="[ %(levelname)s ] %(asctime)s %(filename)s (Line %(lineno)d): %(message)s"
    FORMAT25="[%(levelname)s] %(asctime)s %(module)s.%(funcName)s(): %(message)s"
    FORMAT26=FORMAT25
    FORMAT27=FORMAT26
    
    if major == 2:
        if minor == 4:
            formatstr = FORMAT24
        elif minor == 5:
            formatstr = FORMAT25
        elif minor == 6:
            formatstr = FORMAT26
        elif minor == 7:
            formatstr = FORMAT27
            
    log = logging.getLogger()
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(formatstr)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    # Handle file-based logging.
    if logfile != sys.stderr:
        ensurefile(logfile)        
        hdlr = logging.FileHandler(logfile)
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)

    if warn:
        log.setLevel(logging.WARN)
    if debug: 
        log.setLevel(logging.DEBUG) # Override with command line switches
    if info:
        log.setLevel(logging.INFO) # Override with command line switches
    
    log.debug("%s" %sys.argv)
    if profile:
        log.info("profile %s specified" % profile)
    else:
        '''
        [adhoc]
        workdir=
        tdlonly=
        fileroot=
        target=
        provider=
        credentials=
        templates=
        
        '''
        # Create ad-hoc profile for command line args...
        profile = 'adhoc'
        templates = args
        log.debug("files are %s" % templates)
        config.add_section(profile)
        config.set(profile, 'workdir', workdir )
        config.set(profile, 'fileroot', fileroot )
        config.set(profile, 'templates', ', '.join(templates))
        #config.set(profile, 'target', target )
        #config.set(profile, 'provider', provider )
        #config.set(profile, 'credentials', credentials )        
        
        if tdlonly:
            config.set(profile, 'tdlonly', "True")
        else:
            config.set(profile, 'tdlonly', "False")

        if target:
            config.set(profile, 'target', target )
        else:
            config.set(profile, 'target', 'None' )
        #    config.set(profile, 'target', None )        
        
        if provider:
            config.set(profile, 'provider', provider )
        else:
            config.set(profile, 'provider', 'None' )
        #    config.set(profile, 'provider', None )        

        if credentials:
            config.set(profile, 'credentials', credentials )
        else:
            config.set(profile, 'credentials', 'None' )        
        
        s = "[%s]" % profile
        for option in config.options(profile):
            val = config.get(profile, option)
            s+= " %s=%s " % ( option, val )
        log.debug(s)
    log.debug("Creating ImgFacBuild object...") 
    ifb = ImgFacBuild(config, profile)
    log.debug("Running build...") 
    ifb.build()
    


if __name__ == "__main__": 
    main()
