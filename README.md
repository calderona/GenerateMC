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
Note: this depends on the MC production campaign

4) Launch the gridpacks production
```
python createGridpacks_TrijetRes.py -i template_cards/TrijetRes_g_ggg_BP2_testV1 -n TrijetRes_g_ggg_BP2_testV1
```
* By default jobs are submitted in batch 
* Wait until all the jobs are finished

5) Check and copy gridpacks in new directory
* Gridpacks will be stored by default in *genproductions/bin/MadGraph5_aMCatNLO/*
* Check that all batch jobs are finished successfully
* Copy gridpacks in a new directory
```
mkdir gridpacks/TrijetRes_g_ggg_BP2_testV1
cp genproductions/bin/MadGraph5_aMCatNLO/TrijetRes_g_ggg_BP2_testV1*tarball.tar.xz gridpacks/TrijetRes_g_ggg_BP2_testV1
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
* Copy python hadronizer in the generator folder (use same CMSSW area already prepared at point 6)
```
mkdir -p $CMSSW_BASE/src/Configuration/Generator/python
cp genproductions/python/ThirteenTeV/Hadronizer/Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff.py  $CMSSW_BASE/src/Configuration/Generator/python
```
* Launch script to produce GEN files
```
python makeGENfromLHE.py -v CMSSW_7_1_30 -c Hadronizer_TuneCUETP8M1_13TeV_generic_LHE_pythia8_cff.py -i list.txt -t /tmp/santanas/ --outputDir /eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/
```
* The LHE files are stored in /eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/
```
[santanas@lxplus081 GenerateMC]$ eos ls /eos/cms/store/cmst3/user/santanas/MCsamples/TrijetRes_g_ggg_BP2_testV1/ | grep GEN
TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p1_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
TrijetRes_g_ggg_BP2_testV1_MGKK2000R0p7_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
TrijetRes_g_ggg_BP2_testV1_MGKK5000R0p1_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
TrijetRes_g_ggg_BP2_testV1_MGKK5000R0p7_slc6_amd64_gcc481_CMSSW_7_1_30_GEN.root
```





