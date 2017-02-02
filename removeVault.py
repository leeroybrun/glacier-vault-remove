#!/usr/bin/env python

# -*- coding: UTF-8 -*-

import sys
import json
import time
import os
import logging
import boto3
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
				glacier.delete_archive(
				    vaultName=vaultName,
				    archiveId=archive['ArchiveId']
				)
			except:
				printException()

				logging.info('Sleep 2s before retrying...')
				time.sleep(2)

				logging.info('Retry to remove archive ID : %s', archive['ArchiveId'])
				try:
					glacier.delete_archive(
					    vaultName=vaultName,
					    archiveId=archive['ArchiveId']
					)
					logging.info('Successfully removed archive ID : %s', archive['ArchiveId'])
				except:
					logging.error('Cannot remove archive ID : %s', archive['ArchiveId'])

def printException():
	exc_type, exc_value = sys.exc_info()[:2]
	logging.error('Exception "%s" occured with message "%s"', exc_type.__name__, exc_value)

# Default logging config
logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO, datefmt='%H:%M:%S')

# Get arguments
if len(sys.argv) >= 4:
	accountId = sys.argv[1]
	regionName = sys.argv[2]
	vaultName = sys.argv[3]
else:
	# If there are missing arguments, display usage example and exit
	logging.error('Usage: %s <account_id> <region_name> [<vault_name>|LIST] [DEBUG] [NUMPROCESS]', sys.argv[0])
	sys.exit(1)

# Get custom logging level
if len(sys.argv) == 5 and sys.argv[4] == 'DEBUG':
	logging.info('Logging level set to DEBUG.')
	logging.getLogger().setLevel(logging.DEBUG)

# Get number of processes
numProcess = 1
if len(sys.argv) == 5:
	if sys.argv[4].isdigit():
		numProcess = int(sys.argv[4])
elif len(sys.argv) == 6:
	if sys.argv[5].isdigit():
		numProcess = int(sys.argv[5])
logging.info('Running with %s processes', numProcess)

os.environ['AWS_DEFAULT_REGION'] = regionName

# Load credentials
try:
	f = open('credentials.json', 'r')
	config = json.loads(f.read())
	f.close()

 	os.environ['AWS_ACCESS_KEY_ID'] = config['AWSAccessKeyId']
	os.environ['AWS_SECRET_ACCESS_KEY'] = config['AWSSecretKey']

except:
	logging.error('Cannot load "credentials.json" file... Assuming Role Authentication.')

try:
	logging.info('Connecting to Amazon Glacier...')
	glacier = boto3.client('glacier')
except:
	printException()
	sys.exit(1)

if vaultName == 'LIST':
	try:
		logging.info('Getting list of vaults...')
		response = glacier.list_vaults()
	except:
		printException()
		sys.exit(1)

	for vault in response['VaultList']:
		logging.info(vault['VaultName'])

	exit(0)

try:
	logging.info('Getting selected vault... [{v}]'.format(v=vaultName))
	vault = glacier.describe_vault(vaultName=vaultName)
	logging.info("Working on ARN {arn}".format(arn=vault['VaultARN']))
except:
	printException()
	sys.exit(1)

logging.info('Getting jobs list...')
response = glacier.list_jobs(vaultName=vaultName)
jobID = ''

# Check if a job already exists
for job in response['JobList']:
	if job['Action'] == 'InventoryRetrieval':
		logging.info('Found existing inventory retrieval job...')
		jobID = job['JobId']

if jobID == '':
	logging.info('No existing job found, initiate inventory retrieval...')
	try:
		vault = glacier.Vault(accountId, vaultName)
		job = vault.initiate_inventory_retrieval()

		jobID = job.id
	except:
		printException()
		sys.exit(1)

logging.info('Job ID : %s', jobID)

# Get job status
job = glacier.describe_job(vaultName=vaultName, jobId=jobID)

logging.info('Job Creation Date: {d}'.format(d=job['CreationDate']))

while job['StatusCode'] == 'InProgress':
	# Job are usualy ready within 4hours of request.
	logging.info('Inventory not ready, sleep for 10 mins...')

	time.sleep(60*10)

	job = vault.describe_job(vaultName=vaultName, jobId=jobID)

if job['StatusCode'] == 'Succeeded':
	logging.info('Inventory retrieved, parsing data...')
	job_output = glacier.get_job_output(vaultName=vaultName, jobId=job['JobId'])
	inventory = json.loads(job_output['body'].read().decode('utf-8'))

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
		glacier.delete_vault(
		    vaultName=vaultName
		)
		logging.info('Vault removed.')
	except:
		printException()
		logging.error('We cant remove the vault now. Please wait some time and try again. You can also remove it from the AWS console, now that all archives have been removed.')

else:
	logging.info('Vault retrieval failed.')
