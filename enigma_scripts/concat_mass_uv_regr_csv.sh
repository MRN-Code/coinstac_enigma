#!/bin/bash
#$ -S /bin/bash
 

#----Wrapper for csv version of mass_uv_regr.R script.
#----See readme to change the parameters for your data
#-Dmitry Isaev
#-Boris Gutman
#-Neda Jahanshad
# Beta version for testing on sites.
#-Imaging Genetics Center, Keck School of Medicine, University of Southern California
#-ENIGMA Project, 2015
# enigma@ini.usc.edu 
# http://enigma.ini.usc.edu
#-----------------------------------------------

#---Section 1. Script directories
scriptDir=$1    ## where you have downloaded the ENIGMA Regression R scripts!
resDir=$2   ## directory to be created for your results!
logDir=$3        ## directory to be created to output the log files
DATA_DIR=$4

#---Section 2. Configuration variables-----
RUN_ID="ENIGMA_TEST"
CONFIG_PATH=$5
SITE="MDR"
ROI_LIST_TXT="$resDir/roi_list.txt"

#---Section 5. R binary -- CHANGE this to reflect the full path or your R binary
#Rbin=/usr/local/R-3.1.3/bin/R
Rbin=/usr/bin/R

##############################################################################################
## no need to edit below this line!!
##############################################################################################
#---Section 6. DO NOT EDIT. Running the R script
#go into the folder where the script should be run
if [ ! -d $scriptDir ]
then
   "The script directory you indicated does not exist, please recheck this."
fi

if [ ! -d $resDir ]
then
   "The Results directory you indicated does not exist, please recheck this."
fi

if [ ! -d $logDir ]
then
   "The Log directory you indicated does not exist, please recheck this."
fi


#OUT=$logDir/log_concat.txt
#touch $OUT
cmd="${Rbin} --no-save --slave --args\
		${RUN_ID}\
		${SITE} \
		${logDir} \
		${resDir} \
		${ROI_LIST_TXT} \
		${CONFIG_PATH} \
		${DATA_DIR}
		<  ${scriptDir}/concat_mass_uv_regr.R"
#echo $cmd
#echo $cmd >> $OUT
eval $cmd
