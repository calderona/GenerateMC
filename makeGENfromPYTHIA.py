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
parser = optparse.OptionParser(usage='\nExample: python %prog -n MyProcess -v CMSSW_7_1_30 -c template_pythia_cards/PROCESSNAME_TuneCUETP8M1_13TeV_pythia8_cfi.py -t /tmp/santanas/ --outputDir `pwd`/TestOutput --numberOfevents 1000')
parser.add_option("-n","--genProcessName",action="store",type="string",dest="GENPROCESSNAME",default="")
parser.add_option("-v","--cmsswVersion",action="store",type="string",dest="CMSSWVERSION",default="")
parser.add_option("-c","--pythonConfig",action="store",type="string",dest="PYTHONCONFIG",default="")
parser.add_option("-t","--tmpDir",action="store",type="string",dest="TMPDIR",default="")
parser.add_option("--numberOfevents",action="store",type="string",dest="NEVENTS",default="-1")
parser.add_option("--outputDir",action="store",type="string",dest="OUTPUTDIR",default="")

(options, args) = parser.parse_args()
GENPROCESSNAME = options.GENPROCESSNAME
CMSSWVERSION = options.CMSSWVERSION
PYTHONCONFIG = options.PYTHONCONFIG
TMPDIR = options.TMPDIR
NEVENTS = options.NEVENTS
OUTPUTDIR = options.OUTPUTDIR

if not options.GENPROCESSNAME:   
    parser.error('ERROR: Gen process name is not given')
if not options.CMSSWVERSION:   
    parser.error('ERROR: CMSSW version is not given')
if not options.PYTHONCONFIG:   
    parser.error('ERROR: Input python config is not given')
if not options.TMPDIR:   
    parser.error('ERROR: Tmp directory is not given')
if not options.OUTPUTDIR:   
    parser.error('ERROR: Output directory is not given')

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

# loop over samples
pythonconfignameExt = ((PYTHONCONFIG.split("/")[-1]).split("PROCESSNAME_")[-1]).split(".")[0]
#print pythonconfignameExt

MGKKValues = [500, 4000]
RValues = [0.1, 0.7]
relwidth = 0.01 # 1%

for MGKK in MGKKValues:
    for R in RValues:
        MR = int(MGKK*R)
        print MGKK, R

        Rmod = str(R)   
        Rmod = re.sub("\.","p",Rmod)
        
        CURRENTPROCESS = GENPROCESSNAME+"_"+"M1-"+str(MGKK)+"_R-"+Rmod

        pythonfragment = CURRENTPROCESS+"_"+pythonconfignameExt+".py"
        pythonfilename = CURRENTPROCESS+"_"+pythonconfignameExt+"_GEN.py"
        #print pythonfilename
        outputfilename = CURRENTPROCESS+"_"+pythonconfignameExt+"_GEN.root"
        #print outputfilename

        #create gen fragmet
        outputcard = basedir_path+"/"+CMSSWVERSION+"/src/Configuration/Generator/python/"+pythonfragment
        inputcard = basedir_path+"/"+PYTHONCONFIG

        GENERATETHIS = "'ExcitedFermion:dg2dStar = on',\n'4000001:onMode = off',\n'4000001:onIfMatch = 24 2',\n'4000001:m0 = %s',\n'4000001:mWidth = %s',\n'4000001:doForceWidth = on',\n'24:onMode = off',\n'24:onIfMatch = 1 2',\n'24:m0 = %s',\n'24:mWidth = %s',\n'24:doForceWidth = on',\n'ExcitedFermion:Lambda = %s',\n'ExcitedFermion:coupFprime = 1.',\n'ExcitedFermion:coupF = 1.',\n'ExcitedFermion:coupFcol = 1.'" % (str(MGKK),str(float(MGKK*relwidth)),str(MR),str(float(MR*relwidth)),str(MGKK))

        with open(outputcard, "wt") as fout:            
            with open(inputcard, "rt") as fin:
                for line in fin:
                    ## EDIT CARD
                    line = re.sub("THISPROCESSPARAMETERS",GENERATETHIS,line)                
                    ##
                    fout.write(line)

        print("cmsDriver.py Configuration/Generator/python/%s --fileout %s/%s --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions MCRUN2_71_V1::All --step GEN --magField 38T_PostLS1 --python_filename %s -n %s" % (pythonfragment,TMPDIR,outputfilename,pythonfilename,NEVENTS) )
        os.system("cmsDriver.py Configuration/Generator/python/%s --fileout %s/%s --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions MCRUN2_71_V1::All --step GEN --magField 38T_PostLS1 --python_filename %s -n %s" % (pythonfragment,TMPDIR,outputfilename,pythonfilename,NEVENTS) )

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

