#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import sys
import json
import time
import os.path
import boto.glacier

# Get arguments
regionName = sys.argv[1]
vaultName = sys.argv[2]

# Load credentials
f = open('credentials.json', 'r')
config = json.loads(f.read())
f.close()

print 'Connect to Amazon Glacier...'

glacier = boto.glacier.connect_to_region(regionName, aws_access_key_id=config['AWSAccessKeyId'], aws_secret_access_key=config['AWSSecretKey'])

print 'Get selected vault...'
vault = glacier.get_vault(vaultName)

print 'Get jobs list...'
jobList = vault.list_jobs()
jobID = ''

# Check if 
for job in jobList:
	if job.action == 'InventoryRetrieval':
		print 'Found existing inventory retrieval job...'
		jobID = job.id

if jobID == '':
	print 'No existing job found, initiate inventory retrieval...'
	jobID = vault.retrieve_inventory(description='Python Amazon Glacier Removal Tool')

print 'Job ID : '+ jobID

# Get job status
job = vault.get_job(jobID)

while job.status_code == 'InProgress':
	print 'Inventory not ready, sleep for 30 mins...'

	time.sleep(60*30)

	job = vault.get_job(jobID)

if job.status_code == 'Succeeded':
	print 'Inventory retrieved, parsing data...'
	inventory = json.loads(job.get_output().read())

	print 'Loop over archives...'
	for archive in inventory['ArchiveList']:
		if archive['ArchiveId'] != '':
			print 'Remove archive ID : '+ archive['ArchiveId']
			try:
				vault.delete_archive(archive['ArchiveId'])
			except:
				print 'Error : ', sys.exc_info()[0]

	print 'Removing vault...'
	vault.remove()

	print 'Vault removed.'

else:
	print 'Vault retrieval failed.'