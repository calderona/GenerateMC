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

6) Get generator information from the process
* Create CMSSW area and set environment variables
```
scram p CMSSW_9_2_7
cd CMSSW_9_2_7
cmsenv
cd ..
```
* Create and edit script to extract generator info (use getGenInfo.py as template, depends on the specific model)
```
cp getGenInfo.py getGenInfo_TrijetRes.py
```
* Extract generator info from gridpacks
```
python getGenInfo_TrijetRes.py -i gridpacks/TrijetRes_g_ggg_BP2_testV1 -n TrijetRes_g_ggg_BP2_testV1 -t /tmp/santanas
```
* An output root tree is created in *gridpacks/TrijetRes_g_ggg_BP2_testV1/tree_TrijetRes_g_ggg_BP2_testV1.root* containing some generator level info (below the example for the trijet resonance model):
   * xsec: cross section (pb)
   * gkkmass: KK gluon mass (GeV)
   * gkkwidth: KK gluon width (GeV)
   * gkkbr: KK gluon BR (in the decay of interest: here "Radion+gluon")
   * rmass: Radion mass (GeV)
   * rwidth: Radion width (GeV)
   * rbr: Radion BR (in the decay of interest: here "gluon+gluon")











