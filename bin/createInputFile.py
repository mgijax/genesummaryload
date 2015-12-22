#!/usr/local/bin/python

##########################################################################
#
# Purpose:
#       From mygene input file create assocload input file
#
# Usage: createInputFile.py
# Env Vars:
#	 1. 
#
# Inputs:
#	1. mygene.xml
#	2. Configuration (see genesummaryload.config, assocload.config)
#
# Outputs:
#	 1. tab delimited file in assocload format:
#	    line 1 header: "Entrez Gene" "MyGene"
# 	    1. EntrezGene ID
#           2. MyGene Url Stub (Gene ID)
#	 2. log file
# 
# Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#
#  Assumes:  Nothing
#
#  Notes:  None
#
###########################################################################

import sys
import os
import mgi_utils
import string
import db

print '%s' % mgi_utils.date()

# MyGene logical DB Name
LDBName = os.environ['ASSOC_EXTERNAL_LDB']

# paths to input and two output files
inFilePath = os.environ['INPUT_FILE_DEFAULT']
assocFilePath= os.environ['INPUT_FILE']

# curation log
fpCur = open (os.environ['LOG_CUR'], 'a')

# egIds mapped to organism of associated markers in MGI
#{egId:organism, ...}
egOrgDict = {}

# curator log lists; these records will be reported and skipped
# The MyGene egId is not associated with a marker in MGI
egIdNotInMgiList = []

# The MyGene egId is associated with a non-human marker in MGI
egIdIsNotHumanList = []

# The MyGene url stub is > 30 characters
urlStubGt30CharList = []

# The MyGene url stub contains commas (',')
urlStubContainsCommaList = []

# constants
TAB= '\t'
CRT = '\n'
SPACE = ' '

#
# Initialize
#

jsonDict = eval(open(inFilePath).read())
jsonList = jsonDict['hits']
fpAssocFile = open(assocFilePath, 'w')

results = db.sql('''select a.accid, o.commonName
	from ACC_Accession a, MRK_Marker m, MGI_Organism o
	where a._LogicalDB_key = 55
	and a._MGIType_key = 2
	and a._Object_key = m._Marker_key
	and m._Organism_key = o._Organism_key''', 'auto')

for r in results:
    egOrgDict[r['accid']] = r['commonName']

#
# Process
#

# write out assocload header
fpAssocFile.write('%s%s%s%s' % ('Entrez Gene', TAB, LDBName, CRT))

for dict in jsonList:
    egId = string.strip(str(dict['entrezgene']))
    url_stub = string.strip(dict['wikipedia']['url_stub'])
    if not egOrgDict.has_key(egId):
	egIdNotInMgiList.append('%s %s' % (egId, url_stub))
    elif egOrgDict[egId] != 'human':
	egIdIsNotHumanList.append('%s %s %s' % (egId, url_stub, egOrgDict[egId]))
    elif len(url_stub) > 30:
	urlStubGt30CharList.append('%s %s' % (egId, url_stub))
    elif ',' in url_stub:
	urlStubContainsCommaList.append('%s %s ' % (egId, url_stub))
    else:
	fpAssocFile.write('%s%s%s%s' % (egId, TAB, url_stub, CRT))
    
#
# Post Process
#
if len(egIdNotInMgiList):
    fpCur.write('%sEntrezGene IDs not in MGI%s' % (CRT, CRT))
    fpCur.write('EgId%sUrlStub%s' % (TAB, CRT))
    fpCur.write('------------------------------------------------------------%s' % CRT)
    fpCur.write(string.join(egIdNotInMgiList, CRT))
    fpCur.write(CRT)
    fpCur.write('Total: %s' % len(egIdNotInMgiList))
    fpCur.write(CRT)

if len(egIdIsNotHumanList):
    fpCur.write('%sEntrezGene IDs associated with non-human gene in MGI%s' % (CRT, CRT))
    fpCur.write('EgId%sUrlStub%s' % (TAB, CRT))
    fpCur.write('------------------------------------------------------------%s' % CRT)
    fpCur.write(string.join(egIdIsNotHumanList, CRT))
    fpCur.write(CRT)
    fpCur.write('Total: %s' % len(egIdIsNotHumanList))
    fpCur.write(CRT)

if len(urlStubGt30CharList):
    fpCur.write('%sUrl Stub > 30 characters%s' % (CRT, CRT))
    fpCur.write('EgId%sUrlStub%s' % (TAB, CRT))
    fpCur.write('------------------------------------------------------------%s' % CRT)
    fpCur.write(string.join(urlStubGt30CharList, CRT))
    fpCur.write(CRT)
    fpCur.write('Total: %s' % len(urlStubGt30CharList))
    fpCur.write(CRT)

if len(urlStubContainsCommaList):
    fpCur.write('%sUrl Stub contains a comma%s' % (CRT, CRT))
    fpCur.write('EgId%sUrlStub%s' % (TAB, CRT))
    fpCur.write('------------------------------------------------------------%s' % CRT)
    fpCur.write(string.join(urlStubContainsCommaList, CRT))
    fpCur.write(CRT)
    fpCur.write('Total: %s' % len(urlStubContainsCommaList))
    fpCur.write(CRT)

fpCur.close()
fpAssocFile.close()

print '%s' % mgi_utils.date()
