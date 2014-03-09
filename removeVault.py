#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import sys
import json
import time
import os.path
import logging
import boto.glacier

# Default logging config
logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)

# Get arguments
if len(sys.argv) >= 3:
	regionName = sys.argv[1]
	vaultName = sys.argv[2]
else:
	# If there is missing arguments, display usage example and exit
	logging.error('Usage: %s REGION_NAME VAULT_NAME', sys.argv[0])
	sys.exit(1)

# Get custom logging level
if len(sys.argv) == 4 and sys.argv[3] == 'DEBUG':
	logging.info('Logging level set to DEBUG.')
	logging.basicConfig(level=logging.DEBUG)

# Load credentials
f = open('credentials.json', 'r')
config = json.loads(f.read())
f.close()

try:
	logging.info('Connecting to Amazon Glacier...')
	glacier = boto.glacier.connect_to_region(regionName, aws_access_key_id=config['AWSAccessKeyId'], aws_secret_access_key=config['AWSSecretKey'])
except:
	logging.error(sys.exc_info()[0])
	sys.exit(1)

try:
	logging.info('Getting selected vault...')
	vault = glacier.get_vault(vaultName)
except:
	logging.error(sys.exc_info()[0])
	sys.exit(1)

logging.info('Getting jobs list...')
jobList = vault.list_jobs()
jobID = ''

# Check if a job already exists
for job in jobList:
	if job.action == 'InventoryRetrieval':
		logging.info('Found existing inventory retrieval job...')
		jobID = job.id

if jobID == '':
	logging.info('No existing job found, initiate inventory retrieval...')
	try:
		jobID = vault.retrieve_inventory(description='Python Amazon Glacier Removal Tool')
	except Exception, e:
		logging.error(e)
		sys.exit(1)

logging.debug('Job ID : %s', jobID)

# Get job status
job = vault.get_job(jobID)

while job.status_code == 'InProgress':
	logging.info('Inventory not ready, sleep for 30 mins...')

	time.sleep(60*30)

	job = vault.get_job(jobID)

if job.status_code == 'Succeeded':
	logging.info('Inventory retrieved, parsing data...')
	print vars(job.get_output().read())
	inventory = json.loads(job.get_output().read())

	logging.info('Removing archives... please be patient, this may take some time...');
	for archive in inventory['ArchiveList']:
		if archive['ArchiveId'] != '':
			logging.debug('Remove archive ID : %s', archive['ArchiveId'])
			try:
				vault.delete_archive(archive['ArchiveId'])
			except:
				logging.error(sys.exc_info()[0])

				logging.info('Sleep 2 mins before retrying...')
				time.sleep(60*2)

				logging.info('Retry to remove archive ID : %s', archive['ArchiveId'])
				vault.delete_archive(archive['ArchiveId'])

	logging.info('Removing vault...')
	vault.delete()

	logging.info('Vault removed.')

else:
	logging.info('Vault retrieval failed.')
