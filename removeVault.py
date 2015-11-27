#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import sys
import json
import time
import os.path
import logging
import boto.glacier
from socket import gethostbyname, gaierror

def printException():
	exc_type, exc_value = sys.exc_info()[:2]
	logging.error('Exception "%s" occured with message "%s"', exc_type.__name__, exc_value)

# Default logging config
logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

# Get arguments
if len(sys.argv) >= 3:
	regionName = sys.argv[1]
	vaultName = sys.argv[2]
else:
	# If there is missing arguments, display usage example and exit
	logging.error('Usage: %s <region_name> [<vault_name>|LIST] [DEBUG]', sys.argv[0])
	sys.exit(1)

# Get custom logging level
if len(sys.argv) == 4 and sys.argv[3] == 'DEBUG':
	logging.info('Logging level set to DEBUG.')
	logging.basicConfig(level=logging.DEBUG)

# Load credentials
try:
	f = open('credentials.json', 'r')
	config = json.loads(f.read())
	f.close()
except:
	logging.error('Cannot load "credentials.json" file...')
	printException()
	sys.exit(1)

try:
	logging.info('Connecting to Amazon Glacier...')
	glacier = boto.glacier.connect_to_region(regionName, aws_access_key_id=config['AWSAccessKeyId'], aws_secret_access_key=config['AWSSecretKey'])
except:
	printException()
	sys.exit(1)

if vaultName == 'LIST':
	try:
		logging.info('Getting list of vaults...')
		vaults = glacier.list_vaults()
	except:
		printException()
		sys.exit(1)

	for vault in vaults:
		logging.info(vault.name)

	exit(0)

try:
	logging.info('Getting selected vault...')
	vault = glacier.get_vault(vaultName)
except:
	printException()
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
	except:
		printException()
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
	inventory = json.loads(job.get_output().read().decode('utf-8'))

	logging.info('Removing archives... please be patient, this may take some time...');
	for archive in inventory['ArchiveList']:
		if archive['ArchiveId'] != '':
			logging.debug('Remove archive ID : %s', archive['ArchiveId'])
			try:
				vault.delete_archive(archive['ArchiveId'])
			except:
				printException()

				logging.info('Sleep 2 mins before retrying...')
				time.sleep(60*2)

				logging.info('Retry to remove archive ID : %s', archive['ArchiveId'])
				try:
					vault.delete_archive(archive['ArchiveId'])
					logging.info('Successfully removed archive ID : %s', archive['ArchiveId'])
				except:
					logging.error('Cannot remove archive ID : %s', archive['ArchiveId'])

	logging.info('Removing vault...')
	try:
		vault.delete()
		logging.info('Vault removed.')
	except:
		printException()
		logging.error("We can't remove the vault now. Please wait some time and try again. You can also remove it from the AWS console, now that all archives have been removed.")

else:
	logging.info('Vault retrieval failed.')
