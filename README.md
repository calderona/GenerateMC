# GenerateMC

From a *non-CMSSW* release area on lxplus.cern.ch
```
git clone git@github.com:santanas/GenerateMC.git
```

Clone the official repository for CMS MC production inside *GenerateMC* directory:
```
cd GenerateMC
git clone git@github.com:cms-sw/genproductions.git genproductions
```

## Madgraph production (gridpacks -> LHE -> GEN)

1) Create new directory with template cards for Madgraph
```
mkdir template_cards/TrijetRes_g_ggg_BP2_testV1
cp template_cards/NewModel/* template_cards/TrijetRes_g_ggg_BP2_testV1
```

2) Edit files in template_cards/TrijetRes_g_ggg_BP2_testV1
* PROCESSNAME_customizecards.dat (change default model parameters)
* PROCESSNAME_extramodels.dat (location of new model: zip file should be copied in /afs/cern.ch/cms/generators/www/)
* PROCESSNAME_proc_card.dat (specify the process to be generated)
* PROCESSNAME_run_card.dat (set parameters to run madgraph, usually the same for all processes)

3) Create and edit script for gridpack submission (use createGridpacks.py as template)
```
cp createGridpacks.py createGridpacks_TrijetRes.py
```
* Edit createGridpacks_TrijetRes.py: 
  * specify samples and parameters to be generated (Note: the script should be modified depending on the specific model and this can be taken as example). For the trijet model, just edit these values (i.e. KK gluon mass, mass ratio between Radion and KK gluon):
```
MGKKValues = [2000,5000]
RValues = [0.1,0.7,0.9]
```
* Edit genproductions/bin/MadGraph5_aMCatNLO/gridpack_generation.sh to set the scram_arch and cmssw_version:
```
scram_arch=slc6_amd64_gcc481
cmssw_version=CMSSW_7_1_30
```
Note: this depends on the MC production campaign. Usually you should take the default specified in https://twiki.cern.ch/twiki/bin/view/CMS/QuickGuideMadGraph5aMCatNLO

4) Launch the gridpacks production
```
python createGridpacks_TrijetRes.py -i template_cards/TrijetRes_g_ggg_BP2_testV1 -n TrijetRes_g_ggg_BP2_testV1
```
* By default jobs are submitted in batch 
* Wait until all the jobs are finished

5) Check and copy gridpacks in new directory
* Gridpacks will be stored by default in *genproductions/bin/MadGraph5_aMCatNLO/*
* Check that all batch jobs are finished successfully 
* Resubmit the failed jobs using a command like this one, and then check again
```
./submit_gridpack_generation.sh 15000 50000 1nh TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p1 cards/production/13TeV/TrijetRes_g_ggg_BP2_testV2_MGKK2000R0p1 1nh
```
* Move gridpacks in a new directory
```
mkdir gridpacks/TrijetRes_g_ggg_BP2_testV1
mv genproductions/bin/MadGraph5_aMCatNLO/TrijetRes_g_ggg_BP2_testV1*tarball.tar.xz gridpacks/TrijetRes_g_ggg_BP2_testV1
```

6) Produce LHE file and get generator level information
* Create CMSSW area and set environment variables (same scram arch and cmssw release used to produce gridpacks at point 3)
```
scram p CMSSW_7_1_30
cd CMSSW_7_1_30
cmsenv
cd ..
```
* Create and edit script (use getLHEandGenInfo.py as template, depends on the specific model)
```
cp getLHEandGenInfo.py getLHEandGenInfo_TrijetRes.py
```
* Create LHE files and extract generator info from gridpacks (can also be run without  --createLHE option, in which case only the root tree with gen level info is created)
```
python getLHEandGenInfo_TrijetRes.py -i gridpacks/TrijetRes_g_ggg_BP2_testV1 -n TrijetRes_g_ggg_BP2_testV1 -t /tmp/santanas --getGenInfo --createLHE --numberOfLHEevents 100 --EOSdir /eos/cms/store/cmst3/user/santanas/MCsamples
```
* An output root tree is created in *gridpacks/TrijetRes_g_ggg_BP2_testV1/tree_TrijetRes_g_ggg_BP2_testV1.root* containing some generator level info (below the example for the trijet resonance model):
   * xsec: cross section (pb)
   * gkkmass: KK gluon mass (GeV)
   * gkkwidth: KK gluon width (GeV)
   * gkkbr: KK gluon BR (in the decay of interest: here "Radion+gluon")
   * rmass: Radion mass (GeV)
   * rwidth: Radion width (GeV)
   * rbr: Radion BR (in the decay of interest: here "gluon+gluon")
* The LHE files are stored in the specified eos directory, i.e. in this case */eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1* (together with gen info if --getGenInfo is set)

7) Produce GEN files
* Prepare the list with all the lhe files to be processes:
  * Example of list.txt:
```
root://eoscms///eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p1_slc6_amd64_gcc481_CMSSW_7_1_30.lhe
root://eoscms///eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p7_slc6_amd64_gcc481_CMSSW_7_1_30.lhe
root://eoscms///eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/TrijetRes_g_ggg_BP2_testV1_MGKK5000R0p1_slc6_amd64_gcc481_CMSSW_7_1_30.lhe
root://eoscms///eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/TrijetRes_g_ggg_BP2_testV1_MGKK5000R0p7_slc6_amd64_gcc481_CMSSW_7_1_30.lhe
```
* Setup python hadronizer config (use same CMSSW area already prepared at point 6)
```
cp -r $CMSSW_RELEASE_BASE/src/Configuration/ $CMSSW_BASE/src/
```
* Copy the the specific hadronizer you need (examples below)

Generic: 
```
cp genproductions/python/ThirteenTeV/Hadronizer/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff.py $CMSSW_BASE/src/Configuration/Generator/python
```
Generic plus 1 ISR jet:
```
cp genproductions/python/ThirteenTeV/Hadronizer/Hadronizer_TuneCUETP8M1_13TeV_MLM_5f_max1j_LHE_pythia8_cff.py $CMSSW_BASE/src/Configuration/Generator/python
```
* Then compile
```
cd $CMSSW_BASE/src/
scram b -j8
cd -
```

* Launch script to produce GEN files
```
python makeGENfromLHE.py -v CMSSW_7_1_30 -c Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff.py -i list.txt -t /tmp/santanas/ --outputDir /eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/
```
* The GEN files are stored in /eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/
```
[santanas@lxplus081 GenerateMC]$ eos ls /eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/ | grep GEN
TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p1_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p7_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
TrijetRes_g_ggg_BP2_testV1_MGKK5000R0p1_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
TrijetRes_g_ggg_BP2_testV1_MGKK5000R0p7_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
```

## Pythia production (pythia fragment -> GEN)

1) Setup CMSSW area
```
scram p CMSSW_7_1_30
cd CMSSW_7_1_30
cmsenv
cd ..
```

2) Define template for pythia gen fragment
The standard is: 
```
template_pythia_cards/PROCESSNAME_TuneCUETP8M1_13TeV_pythia8_cfi.py
```
The line with THISPROCESSPARAMETERS will be replaced with the actual pythia instructions by the following script

3) Create and edit script for config file production (use makeGENfromPYTHIA.py as template)
```
cp makeGENfromPYTHIA.py makeGENfromPYTHIA_Res1ToRes2QTo3Q.py
```
* Edit makeGENfromPYTHIA_Res1ToRes2QTo3Q.py: 
  * specify samples and parameters to be generated (Note: the script should be modified depending on the specific model and this can be taken as example). For the trijet model, just edit these values (i.e. Res1 mass, mass ratio between Res2 and Res1, and relative width of Res1 and Res2 - the same):
```
MGKKValues = [500, 4000]
RValues = [0.1, 0.7]
relwidth = 0.01 # 1%
```
  * if you just want to produce the config files - without producing the GEN .root files - you should add 
```
--no_exec
```
in these lines (at the end, inside the quotation marks):
```
print("cmsDriver.py Configuration/Generator/python/%s --fileout %s/%s --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions MCRUN2_71_V1::All --step GEN --magField 38T_PostLS1 --python_filename %s -n %s" % (pythonfragment,TMPDIR,outputfilename,pythonfilename,NEVENTS) )
os.system("cmsDriver.py Configuration/Generator/python/%s --fileout %s/%s --mc --eventcontent RAWSIM --datatier GEN-SIM --conditions MCRUN2_71_V1::All --step GEN --magField 38T_PostLS1 --python_filename %s -n %s" % (pythonfragment,TMPDIR,outputfilename,pythonfilename,NEVENTS) )
```

4) Launch the gen production
```
python makeGENfromPYTHIA_Res1ToRes2QTo3Q.py -n Res1ToRes2QTo3Q -v CMSSW_7_1_30 -c template_pythia_cards/PROCESSNAME_TuneCUETP8M1_13TeV_pythia8_cfi.py -t /tmp/santanas --outputDir /eos/cms/store/cmst3/user/santanas/MCsamples/Res1ToRes2QTo3Q --numberOfevents 1000
```
* Jobs are processed one after the other, in local
* The output directory can be on eos or in local (afs) directory
* The gen fragments are in $CMSSW_BASE/src/ (these files should be provided to gen group for official production)
* The final configuration files are in $CMSSW_BASE/src/Configuration/Generator/python/ (these are used to generate privately the GEN .root files in this step)
