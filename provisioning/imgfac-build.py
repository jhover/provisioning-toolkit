#!/bin/env python
#
#
# Top level build tool
#
# imgfac-build  TDL_FILE  [ TDL_FILE ]
#
# Execute with one or more TDL files. 
#  
# For each <filename>.tdl checks to see if there is a <filename>.files.yaml
# If so, it runs embed-files against the yaml, creating <filename>.files.tdl 
#
# It then runs merge-tdl agains each <filename>.tdl and <filename>.files.tdl to produce <filename>.withfiles.tdl
#
# It then runs merge-tdls against all <filename>.withfiles.tdl in order, with later TDLs overriding earlier where
# there are collisions. Latter TDLs override equivalent content in earlier TDLs. 
#
# It then runs 
# imagefactory 
#   --verbose target_image 
#   --template work/sl6-x86_64-base-batch-osg-atlas.tdl openstack-kvm
#
# captures the resulting UUID of the build, then uploads using glance:
# 
# glance image-create 
#    --name sl6-x86_64-wn-atlas 
#    --disk-format raw 
#    --container-format bare 
#    --file /home/imagefactory/lib/storage/7260bef6-3409-4d22-8211-a4e91072d7c0.body 
#    --is-public False
#
#  os.path.exists()
#
#  p = subprocess.Popen(querycmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)     
#  out = None
#  (out, err) = p.communicate()
#  self.log.debug('querycondor: it took %s seconds to perform the query' %delta)
#  self.log.debug('out = %s' % out)
#  os.path.realpath(path)
#



from __future__ import print_function
import getopt
import logging
import os
import shutil
import StringIO
import sys
import subprocess
import time


class ImgFacBuild(object):
    
    def __init__(self, config, profile):
        self.log = logging.getLogger()
        self.config = config
        self.profile = profile
        self.tdlonly = config.get(profile,'tdlonly')
        
        
    def build(self, files):
        if files:
            handle_embedfiles(files)
            make_withfiles(files)
            finaltdl = handle_mergetdls(files)
        if not tdlonly:
            run_imagefactory(finaltdl)
        else:
            self.log.info("Final TDL produced at: %s" % finaltdl)
            self.log.debug("TDL only requested. No build.")


    def handle_embedfiles(self, files):
        '''
        Takes a files.yaml file for each name and creates a files.tdl for later merging. 
        '''
        for f in files:
            name = getname(f)
            ext = getext(f)
            p = getpathdir(f)
            self.log.info("Embedding files. Handling %s" % f)
            self.log.debug("Handling path=%s name=%s ext=%s" % (p, name, ext))
            yamlfile = "%s.files.yaml" % name
            self.log.debug("yamlfile=%s" % yamlfile )
            yfp = "%s/%s" % (p, yamlfile)
            self.log.debug("checking if %s exists..." % yfp  ) 
            destname = "%s/%s.files.tdl" % (tempdir,name)
            if os.path.exists(yfp):
                self.log.debug("yep. running embed_files...")
                cmd = "embed-files -o %s --fileroot %s %s " % ( destname, fileroot, yfp)
                self.log.debug("command: %s" % cmd)
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                (out, err) = p.communicate()
                self.log.debug('out = %s' % out)
                self.log.debug('err = %s' % err)
            else:
                self.log.debug("No <name>.files.yaml file so doing nothing.")
    
    def make_withfiles(self, files):
        '''
        Combine all <name>.files.tdl and <name>.tdl files into <name>.withfiles.tdl
            '''
        for f in files:
            name = getname(f)
            ext = getext(f)
            p = getpathdir(f)
            self.log.info("Handling %s" % f)                  
            self.log.debug("Handling path=%s name=%s ext=%s" % (p, name, ext))
            wfp = "%s/%s.files.tdl" % (tempdir,name)
            destname = "%s/%s.withfiles.tdl" % (tempdir,name)
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
    
    
    def handle_mergetdls(self, files):
        '''
        Combine all <name>.withfiles.tdl into final tdl named
          <name1>-<name2>-<nameN>.tdl
        Return name of final tdl file path. 
        '''
        withfiles = []
        destname = ""
        for f in files:
            name = getname(f)
            ext = getext(f)
            p = getpathdir(f) 
            self.log.info("Handling %s" % f)
            wfp = "%s/%s.withfiles.tdl" % (tempdir,name)
            withfiles.append(wfp)
            if destname == "":
                destname = "%s" % name
            else:
                destname = "%s-%s" % (destname, name)
        
        self.log.debug("withfiles is %s" % withfiles)
        allfiles = " ".join(withfiles)
        cmd = "merge-tdls -o %s/%s.tdl %s" % (tempdir, destname, allfiles )
        self.log.debug("command= %s" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (out, err) = p.communicate()
        self.log.debug('err = %s' % err)
        self.log.debug('out = %s' % out)
        retval = "%s/%s.tdl" % (tempdir, destname)
        self.log.debug('returning %s'% retval)
        return retval
    
    
    def run_imagefactory(self, tdlfile):
        self.log.info("Running imagefactory base...")
        (status, uuid) = run_imagefactory_base(tdlfile)
        self.log.info("Ran imagefactory base...") 
        if uuid is not None and target is not None:
            (status,uuid) = run_imagefactory_target(uuid, target)
        self.log.info("Ran imagefactory target...")
    
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
        self.log.debug("cmd is %s" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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
        (out, err) = p.communicate()
        self.log.debug('out = %s' % out)
        self.log.debug('err = %s' % err)
        (status, uuid) = parse_imagefactory_return(out)
        return (status,uuid)
        
    
    def run_imagefactory_target(self, uuid):
        cmd = "time imagefactory --debug target_image --id %s %s " % (uuid, target)
        self.log.info("Running imagefactory: '%s'" % cmd)
        self.log.debug("cmd is %s" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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
        (out, err) = p.communicate()
        self.log.debug('out = %s' % out)
        self.log.debug('err = %s' % err)
        (status, uuid) = parse_imagefactory_return(out)
        
        if status is not None: 
            if target == 'openstack-kvm':
                print("glance --verbose image-create --name name --disk-format raw --container-format bare --file /home/imagefactory/lib/storage/%s.body --is-public False" % uuid)
            elif target == 'ec2':
                print("imagefactory provider_image --id %s ec2 @us-east-1 ec2_credentials.xml" % uuid)
        else:
            self.log.warning("imagefactory had error: %s" % err)

    def run_imagefactory_provider(self, uuid):
        cmd = "time imagefactory --%s provider_image --id %s %s " % (self.loglevel, uuid, self.target, self.credential)
        self.log.info("Running imagefactory: '%s'" % cmd)
        self.log.debug("cmd is %s" % cmd)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
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
        (out, err) = p.communicate()
        self.log.debug('out = %s' % out)
        self.log.debug('err = %s' % err)
        (status, uuid) = parse_imagefactory_return(out)
        
        if status is not None: 
            if target == 'openstack-kvm':
                print("glance --verbose image-create --name name --disk-format raw --container-format bare --file /home/imagefactory/lib/storage/%s.body --is-public False" % uuid)
            elif target == 'ec2':
                print("imagefactory provider_image --id %s ec2 @us-east-1 ec2_credentials.xml" % uuid)
        else:
            self.log.warning("imagefactory had error: %s" % err)


def parse_imagefactory_return(text):
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
        raise Exception("All input files must hav .%s extension." % ext)



def main():
    
    global log
    global tempdir
    global fileroot
    global target
    global tdlonly 
    
    debug = 0
    info = 0
    warn = 0
    tdlonly = 0
    logfile = sys.stderr
    outfile = sys.stdout
    tempdir = os.path.expanduser("~/tmp")
    target = None
    config_file = None
    default_configfile = os.path.expanduser("~/etc/imgfac.conf")
    profile = None
    
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
                                   "hdvc:t:r:L:o:t:w:Tp:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "config=",
                                    "tempdir=",
                                    "fileroot=",
                                    "logfile=",
                                    "outfile=",
                                    "target=",
                                    "workdir=",
                                    "tdl",
                                    "profile",
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
            debug = 1
        elif opt in ("-v", "--verbose"):
            info = 1
        elif opt in ("-c", "--config"):
            config_file = arg
        elif opt in ("-L","--logfile"):
            logfile = arg
        elif opt in ("-r","--fileroot"):
            fileroot = arg
        elif opt in ("-w", "--workdir"):
            tempdir = arg               
        elif opt in ("-T", "--tdl"):
            tdlonly = 1
        elif opt in ("-p", "--profile"):
            profile = arg

    # Read in config file
    config=ConfigParser()
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
        profile = 'adhoc'
        files = args
        log.debug("files are %s" % files)
        config.add_section(profile)
        #
        # workdir fileroot templates
        #
        #
        config.set(profile, 'workdir', '15')
        #config.
  
    ifb = ImgFacBuild(config, profile)



if __name__ == "__main__": 
    main()
