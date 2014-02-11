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
#  log.debug('querycondor: it took %s seconds to perform the query' %delta)
#  log.debug('out = %s' % out)
#  os.path.realpath(path)
#



from __future__ import print_function
import getopt
import logging
import os
import shutil
import sys
import subprocess
import time



def handle_embedfiles(files):
    '''
    Takes a files.yaml file for each name and creates a files.tdl for later merging. 
    '''
    for f in files:
        name = getname(f)
        ext = getext(f)
        p = getpathdir(f)
        log.debug("Handling path=%s name=%s ext=%s" % (p, name, ext))
        yamlfile = "%s.files.yaml" % name
        log.debug("yamlfile=%s" % yamlfile )
        yfp = "%s/%s" % (p, yamlfile)
        log.debug("checking if %s exists..." % yfp  ) 
        destname = "%s/%s.files.tdl" % (tempdir,name)
        if os.path.exists(yfp):
            log.debug("yep. running embed_files...")
            cmd = "embed-files -o %s --fileroot %s %s " % ( destname, fileroot, yfp)
            log.debug("command: %s" % cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (out, err) = p.communicate()
            log.debug('out = %s' % out)
            log.debug('err = %s' % err)
        else:
            log.debug("No <name>.files.yaml file so doing nothing.")

def make_withfiles(files):
    '''
    Combine all <name>.files.tdl and <name>.tdl files into <name>.withfiles.tdl
        '''
    for f in files:
        name = getname(f)
        ext = getext(f)
        p = getpathdir(f)                  
        log.debug("Handling path=%s name=%s ext=%s" % (p, name, ext))
        wfp = "%s/%s.files.tdl" % (tempdir,name)
        destname = "%s/%s.withfiles.tdl" % (tempdir,name)
        if os.path.exists(wfp):
            log.debug("yep. running merge-tdls...")
            cmd = "merge-tdls -o %s %s %s " % ( destname, f, wfp )
            log.debug("command= %s" % cmd)
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (out, err) = p.communicate()
            log.debug('out = %s' % out)
            log.debug('err = %s' % err)
        else:
            log.debug("No <name>.files.tdl so copying <name>.tdl to <name>.withfiles.tdl...")
            shutil.copy(f, destname)
            log.debug("copied %s -> %s" % (f,destname))


def handle_mergetdls(files):
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
        log.debug("Handling %s" % f)
        wfp = "%s/%s.withfiles.tdl" % (tempdir,name)
        withfiles.append(wfp)
        if destname == "":
            destname = "%s" % name
        else:
            destname = "%s-%s" % (destname, name)
    
    log.debug("withfiles is %s" % withfiles)
    allfiles = " ".join(withfiles)
    cmd = "merge-tdls -o %s/%s.tdl %s" % (tempdir, destname, allfiles )
    log.debug("command= %s" % cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (out, err) = p.communicate()
    log.debug('err = %s' % err)
    log.debug('out = %s' % out)
    retval = "%s/%s.tdl" % (tempdir, destname)
    log.debug('returning %s'% retval)
    return retval

 

def run_imagefactory(tdlfile):
    '''
out:    
============ Final Image Details ============
UUID: aee9b860-c067-4ad8-8622-55a785dd96f4
Type: target_image
Status: COMPLETE
Status Details: {'error': None, 'activity': 'Target Image build complete'}
   
    '''
    cmd = "time imagefactory --verbose target_image --template %s openstack-kvm " % tdlfile
    log.debug("cmd is %s" % cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    sec = 0
    retcode = None
    INTERVAL = 30
    while retcode is None:
        retcode = p.poll()
        time.sleep(INTERVAL)
        sec = sec + INTERVAL
        if sec < 60:        
            log.debug("%s seconds elapsed..." % sec)
        else:
            min =  sec / 60
            secmod = sec % 60
            log.debug("%s min %s sec elapsed..." % (min, secmod))  
    (out, err) = p.communicate()
    log.debug('out = %s' % out)
    log.debug('err = %s' % err)
    (status, uuid) = parse_imagefactory_return(out)
    if status is not None:
        print("glance --verbose image-create --name name --disk-format raw --container-format bare --file /home/imagefactory/lib/storage/%s.body --is-public False" % uuid)
    else:
        print("imagefactory had error: %s" % err)

def parse_imagefactory_return(text):
    uuid = None
    status = None
    for line in text:
        if line[0:4] == 'UUID':
            uuid = line[6:]
            
        if line[0:6] == 'Status':
            s = line[8:] 
            if s == 'COMPLETE':
                status = True
    if uuid is not None and status is not None:
        log.debug("parsed UUID: %s" % uuid)
        return (status, uuid)
    else:
        log.debug("failed to parse UUID from text: %s" % text)
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
    
    
    debug = 0
    info = 0
    warn = 0
    logfile = sys.stderr
    outfile = sys.stdout
    tempdir = os.path.expanduser("~/tmp")
    
    usage = """Usage: imgfac-build.py [OPTIONS] TDL  [TDL2  FILE3 ] 
   merge-tdls takes multiple TDLs and merges them, with later TDLs overriding earlier ones. 
   OPTIONS: 
        -h --help                   Print this message
        -d --debug                  Debug messages
        -v --verbose                Verbose messages
        -L --logfile                STDERR
        -r --fileroot               <working directory>
        -V --version                Print program version and exit.
        -o --outfile                STDOUT
        
     """

    # Handle command line options
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, 
                                   "hdvt:r:L:o:", 
                                   ["help", 
                                    "debug", 
                                    "verbose",
                                    "tempdir=",
                                    "fileroot=",
                                    "logfile=",
                                    "outfile=",
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
        elif opt in ("-L","--logfile"):
            logfile = arg
        elif opt in ("-r","--fileroot"):
            fileroot = arg
        elif opt in ("-t", "--tempdir"):
            tempdir = arg
               
    
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
    files = args
    log.debug(files)

    if files:
        handle_embedfiles(files)
        make_withfiles(files)
        finaltdl = handle_mergetdls(files)
        run_imagefactory(finaltdl)
        

if __name__ == "__main__": 
    main()