#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import sys
import json
import time
import os.path
import boto.glacier
from __future__ import print_function

jobIDfile = '/tmp/glacierRemoveJobID'

# Get arguments
regionName = sys.argv[1]
vaultName = sys.argv[2]

# Load credentials
config = json.loads(open('credentials.json').read())

print 'Connect to Amazon Glacier...'

glacier = boto.glacier.connect_to_region(regionName, aws_access_key_id=config['AWSAccessKeyId'], aws_secret_access_key=config['AWSSecretKey'])

print 'Get selected vault...'
vault = glacier.get_vault(vaultName)

if len(sys.argv) == 4:
	print 'Get job ID from args...'
	jobID = sys.argv[3]
elif os.path.isfile(jobIDfile):
	print 'Get job ID from file...'
	jobFile = open(jobIDfile, 'r')
	jobID = jobFile.read()
	jobFile.close()
else:
	print 'Initiate inventory retrieval job...'
	jobID = vault.retrieve_inventory(description='Python Amazon Glacier Removal Tool')

print 'Job ID : '+ jobID

print(jobID, file=jobIDfile)

# Get job status
job = vault.get_job(jobID)

while job.status_code == 'InProgress':
	print 'Inventory not ready, sleep for 30 mins...'

	time.sleep(60*30)

	job = vault.get_job(jobID)

if job.status_code == 'Succeeded':
	print 'Inventory retrieved, parsing data...'
	inventory = json.loads(job.get_output())

	print 'Loop over archives...'
	for archive in inventory['ArchiveList']:
		print 'Remove archive ID : '+ archive['ArchiveId']
		vault.delete_archive(archive['ArchiveId'])

	print 'Removing vault...'
	vault.remove()

	print 'Vault removed.'

else:
	print 'Vault retrieval failed.'