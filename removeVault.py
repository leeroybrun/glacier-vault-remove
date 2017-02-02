#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import sys
import json
import time
import os
import logging
import boto.glacier
from multiprocessing import Process
from socket import gethostbyname, gaierror

def split_list(alist, wanted_parts=1):
	length = len(alist)
	return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
		for i in range(wanted_parts) ]

def process_archive(archive_list):
	logging.info('Starting work on %s items', len(archive_list))
	for index, archive in enumerate(archive_list):
		if archive['ArchiveId'] != '':
			logging.info('%s Remove archive number %s of %s, ID : %s', os.getpid(), index, len(archive_list), archive['ArchiveId'])
			try:
				vault.delete_archive(archive['ArchiveId'])
			except:
				printException()

				logging.info('Sleep 2s before retrying...')
				time.sleep(2)

				logging.info('Retry to remove archive ID : %s', archive['ArchiveId'])
				try:
					vault.delete_archive(archive['ArchiveId'])
					logging.info('Successfully removed archive ID : %s', archive['ArchiveId'])
				except:
					logging.error('Cannot remove archive ID : %s', archive['ArchiveId'])

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
	# If there are missing arguments, display usage example and exit
	logging.error('Usage: %s <region_name> [<vault_name>|LIST] [DEBUG] [NUMPROCESS]', sys.argv[0])
	sys.exit(1)

# Get custom logging level
if len(sys.argv) == 4 and sys.argv[3] == 'DEBUG':
	logging.info('Logging level set to DEBUG.')
	logging.getLogger().setLevel(logging.DEBUG)

# Get number of processes
numProcess = 1
if len(sys.argv) == 4:
	if sys.argv[3].isdigit():
		numProcess = int(sys.argv[3])
elif len(sys.argv) == 5:
	if sys.argv[4].isdigit():
		numProcess = int(sys.argv[4])
logging.info('Running with %s processes', numProcess)

# Load credentials
connection_kwargs = {}
try:
	f = open('credentials.json', 'r')
	config = json.loads(f.read())
	f.close()

	connection_kwargs['aws_access_key_id'] = config['AWSAccessKeyId']
	connection_kwargs['aws_secret_access_key'] = config['AWSSecretKey']

except:
	logging.error('Cannot load "credentials.json" file... Assuming Role Authentication.')

try:
	logging.info('Connecting to Amazon Glacier...')
	glacier = boto.glacier.connect_to_region(regionName, **connection_kwargs)
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
	logging.info('Getting selected vault... [{v}]'.print(v=vaultName))
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

logging.info('Job ID : %s', jobID)

# Get job status
job = vault.get_job(jobID)

logging.info('Job Creation Date: {d}'.format(d=job.creation_date))

while job.status_code == 'InProgress':
	# Job are usualy readyn within 4hours of request.
	logging.info('Inventory not ready, sleep for 10 mins...')

	time.sleep(60*10)

	job = vault.get_job(jobID)

if job.status_code == 'Succeeded':
	logging.info('Inventory retrieved, parsing data...')
	inventory = json.loads(job.get_output().read().decode('utf-8'))

	archiveList = inventory['ArchiveList']

	logging.info('Removing %s archives... please be patient, this may take some time...', len(archiveList));
	archiveParts = split_list(archiveList, numProcess)
	jobs = []

	for archive in archiveParts:
		p = Process(target=process_archive, args=(archive,))
		jobs.append(p)
		p.start()

	for j in jobs:
		j.join()

	logging.info('Removing vault...')
	try:
		vault.delete()
		logging.info('Vault removed.')
	except:
		printException()
		logging.error('We cant remove the vault now. Please wait some time and try again. You can also remove it from the AWS console, now that all archives have been removed.')

else:
	logging.info('Vault retrieval failed.')
