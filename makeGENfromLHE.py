#!usr/bin/python
import os
import optparse 
import sys 
import subprocess
import datetime 
import re
from subprocess import check_output
import ROOT
import numpy as nn
from random import randint

basedir_path = os.path.dirname(os.path.realpath(__file__))
print basedir_path

usage = ""
parser = optparse.OptionParser(usage='\nExample: python %prog -v CMSSW_7_1_30 -c Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff.py -i list.txt -t /tmp/santanas/ --outputDir `pwd`/TestOutput')
parser.add_option("-v","--cmsswVersion",action="store",type="string",dest="CMSSWVERSION",default="")
parser.add_option("-c","--pythonConfig",action="store",type="string",dest="PYTHONCONFIG",default="")
parser.add_option("-i","--inputLHEList",action="store",type="string",dest="INPUTLHELIST",default="")
parser.add_option("-t","--tmpDir",action="store",type="string",dest="TMPDIR",default="")
parser.add_option("--numberOfevents",action="store",type="string",dest="NEVENTS",default="-1")
parser.add_option("--outputDir",action="store",type="string",dest="OUTPUTDIR",default="")

(options, args) = parser.parse_args()
CMSSWVERSION = options.CMSSWVERSION
PYTHONCONFIG = options.PYTHONCONFIG
INPUTLHELIST = options.INPUTLHELIST
TMPDIR = options.TMPDIR
NEVENTS = options.NEVENTS
OUTPUTDIR = options.OUTPUTDIR

if not options.CMSSWVERSION:   
    parser.error('ERROR: CMSSW version is not given')
if not options.PYTHONCONFIG:   
    parser.error('ERROR: Input python config is not given')
if not options.INPUTLHELIST:   
    parser.error('ERROR: Input LHE list is not given')
if not options.TMPDIR:   
    parser.error('ERROR: Tmp directory is not given')
if not options.OUTPUTDIR:   
    parser.error('ERROR: Output directory is not given')

#get list of lhe files
proc = subprocess.Popen(["less %s" % INPUTLHELIST], stdout=subprocess.PIPE, shell=True)
(lhefilelist, err) = proc.communicate()
lhefilelist = lhefilelist.splitlines()
print lhefilelist

#create output dir
IsEosDir = False
if ("/eos/" in OUTPUTDIR):
    print "IS EOS DIR"
    IsEosDir = True
else:
    print "IS NOT EOS DIR"
    IsEosDir = False

if IsEosDir:
    print("eos mkdir -p %s" % (OUTPUTDIR) )
    os.system("eos mkdir -p %s" % (OUTPUTDIR) )
else:
    print("mkdir -p %s" % (OUTPUTDIR) )
    os.system("mkdir -p %s" % (OUTPUTDIR) )

os.chdir("%s/src" % (CMSSWVERSION))

# loop over gripacks
for lhefile in lhefilelist:

    outputfilename = ((lhefile.split("/")[-1]).split("."))[0]+"_GEN.root"
    #print outputfilename
    pythonfilename = ((lhefile.split("/")[-1]).split("."))[0]+"_GEN.py"
    #print pythonfilename

    print("cmsDriver.py Configuration/Generator/python/%s --filein %s --fileout %s/%s --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions MCRUN2_71_V1::All --step GEN --magField 38T_PostLS1 --python_filename %s -n %s" % (PYTHONCONFIG,lhefile,TMPDIR,outputfilename,pythonfilename,NEVENTS) )
    os.system("cmsDriver.py Configuration/Generator/python/%s --filein %s --fileout %s/%s --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions MCRUN2_71_V1::All --step GEN --magField 38T_PostLS1 --python_filename %s -n %s" % (PYTHONCONFIG,lhefile,TMPDIR,outputfilename,pythonfilename,NEVENTS) )

    # move output in final directory
    if IsEosDir:
        TMPFILE = ("%s/%s" % (TMPDIR,outputfilename))
        TMPFILE = re.sub("//","/",TMPFILE) 
        OUTPUTFILE = ("%s/%s" % (OUTPUTDIR,outputfilename))
        OUTPUTFILE = re.sub("//","/",OUTPUTFILE) 

        print("eos cp %s %s" % (TMPFILE,OUTPUTFILE))
        os.system("eos cp %s %s" % (TMPFILE,OUTPUTFILE))
        print("rm -f %s" % (TMPFILE))
        os.system("rm -f %s" % (TMPFILE))
    else:
        print("mv %s/%s %s/%s" % (TMPDIR,outputfilename,OUTPUTDIR,outputfilename))
        os.system("mv %s/%s %s/%s" % (TMPDIR,outputfilename,OUTPUTDIR,outputfilename))

os.chdir("%s" % (basedir_path))

