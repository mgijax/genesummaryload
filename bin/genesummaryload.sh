#!/bin/sh
#
#  genesummaryload.sh
###########################################################################
#
#  Purpose:
# 	This script parses input file, creates assocload
#       input file and invokes assocload
#
  Usage=genesummaryload.sh
#
#  Env Vars:
#
#      See the configuration file
#
#  Inputs:
#
#      - Common configuration file -
#               /usr/local/mgi/live/mgiconfig/master.config.sh
#      - Load configuration file - genesummaryload.config
#      - input file - see python script header
#
#
#  Outputs:
#
#      - An archive file
#      - Log files defined by the environment variables ${LOG_PROC},
#        ${LOG_DIAG}, ${LOG_CUR} and ${LOG_VAL}
#      - Input files for assocload
#      - see assocload outputs
#      - Records written to the database tables
#      - Exceptions written to standard error
#      - Configuration and initialization errors are written to a log file
#        for the shell script
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  Fatal error occurred
#      2:  Non-fatal error occurred
#
#  Assumes:  Nothing
#
# History:
#
# sc	11/30/2015 - created
#

cd `dirname $0`
LOG=`pwd`/genesummaryload.log
rm -rf ${LOG}

CONFIG_LOAD=../genesummaryload.config

#
# verify & source the configuration file
#

if [ ! -r ${CONFIG_LOAD} ]
then
    echo "Cannot read configuration file: ${CONFIG_LOAD}"
    exit 1
fi

. ${CONFIG_LOAD}

#
#  Source the DLA library functions.
#

if [ "${DLAJOBSTREAMFUNC}" != "" ]
then
    if [ -r ${DLAJOBSTREAMFUNC} ]
    then
        . ${DLAJOBSTREAMFUNC}
    else
        echo "Cannot source DLA functions script: ${DLAJOBSTREAMFUNC}" | tee -a ${LOG}
        exit 1
    fi
else
    echo "Environment variable DLAJOBSTREAMFUNC has not been defined." | tee -a ${LOG}
    exit 1
fi

#####################################
#
# Main
#
#####################################
# remove logs (if not assocload logs will be appended)
cleanDir ${LOGDIR}

#
# createArchive including OUTPUTDIR, startLog, getConfigEnv
# sets "JOBKEY"

preload ${OUTPUTDIR} ${INPUTDIR}

# remove files from output directory
cleanDir ${OUTPUTDIR}

#
# Create assocload input file
#
echo "Creating Gene Summary association load input file" >> ${LOG_DIAG}
${GENESUMMARYLOAD}/bin/createInputFile.py >> ${LOG_DIAG}
STAT=$?
checkStatus ${STAT} "createInputFile.py"

#
# run association load
#

# set to full path for assocload
CONFIG_LOAD=${GENESUMMARYLOAD}/assocload.config

echo "Running Gene Summary association load" >> ${LOG_DIAG}
echo "${ASSOCLOADER_SH} ${CONFIG_LOAD} ${JOBKEY}"
${ASSOCLOADER_SH} ${CONFIG_LOAD} ${JOBKEY}
STAT=$?
checkStatus ${STAT} "${ASSOCLOADER_SH} ${CONFIG_LOAD}"

#
# run postload cleanup and email logs
#
shutDown
