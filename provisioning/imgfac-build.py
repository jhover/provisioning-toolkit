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



def handle_embedfiles(files):
    '''
    Takes a files.yaml file for each name and creates a files.tdl for later merging. 
    '''
    
    
    for f in files:
        p = os.path.dirname(f)
        fn = os.path.basename(f)
        #os.path.realpath(path)
        log.debug("base %s  file %s" % (p,fn))
        log.debug("filepath %s/%s"% (p,fn) )
        (name, ext) = nameext(fn)
        yamlfile = "%s.files.yaml" % name
        yamlfilepath = "%s/%s" % (p, yamlfile)
        log.debug("checking if %s exists...") % yamlfilepath
        destname = "%s/%s.files.tdl" % (tempdir,p,name)
        if os.path.exists(yamlfilepath):
            log.debug("yep. running embed_files...")
            cmd = "embed-files -o %s --fileroot %s %s " % ( destname, fileroot, yamlfilepath)
            log.debug("command: %s" % cmd)
            
        else:
            log.debug("nope. copying tdl to X.files.tdl")

            log.debug("copying %s to %s" % (f,destname))
            shutil.copyfile(f, destname)
        
              

def handle_mergetdls(files):
    for f in files:
        (p, fn) = os.path.split(f)
        log.debug("base %s  file %s" % (p,fn))


def run_imagefactory(tdlfile):
    log.debug("imagefactory --verbose target_image --template  openstack-kvm ")
    

def nameext(filename):
        ext = filename.split('.')[-1:]
        name = '.'.join(filename.split('.')[:-1])
        return(name, ext)
    


def main():
    
    global log
    global tempdir
    
    
    debug = 0
    info = 0
    warn = 0
    logfile = sys.stderr
    outfile = sys.stdout
    tmpdir = os.path.expanduser("~/tmp/")
    
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
        finaltdl = handle_mergetdls(files)
        run_imagefactory(finaltdl)
        

if __name__ == "__main__": 
    main()