glacier-vault-remove
======================

This tool can help you remove an Amazon Glacier vault, even if it's not empty.

It will remove all archives contained inside the vault, and then remove the vault itself.

It is intended to work well with vaults containing a lot of archives. I developed it because my vault contained more than 500'000 archives, and all other softwares crashed when I tried to remove all of them.

## Install

### Docker

If you have docker installed, you can easily run the script using the [`leeroyb/glacier-vault-remove`](https://hub.docker.com/r/leeroyb/glacier-vault-remove) image available on Docker Hub:

```
docker run -v /ABSOLUTE_LOCAL_PATH_TO/credentials.json:/app/credentials.json -D leeroyb/glacier-vault-remove <region-name> [<vault-name>|LIST] [DEBUG] [NUM_PROCESSES] [<job_id>|LIST|NEW|LATEST]
```

Make sure you use the _full_ absolute path to `credentials.json` (see below), relative paths do not work here.

### Without Docker

You can clone or [download this repository](https://github.com/leeroybrun/glacier-vault-remove/archive/master.zip) and install the dependencies (boto3) by calling the install script :

```shell
python setup.py install
```

## Configure

Then create a `credentials.json` file in the same directory as `removeVault.py` (or anywhere on your filesystem if using Docker) :

```json
{
	"AWSAccessKeyId": "YOURACCESSKEY",
	"AWSSecretKey":   "YOURSECRETKEY"
}
```

## Use

You can then use the script like this :

```shell
python removeVault.py <region-name> [<vault-name>|LIST] [DEBUG] [NUM_PROCESSES] [<job_id>|LIST|NEW|LATEST]
```

Example :

```shell
python removeVault.py eu-west-1 my_vault
```

### Multiple processes

If you want to perform the removal using multiple processes (4 processes here) :

```shell
python removeVault.py <region-name> <vault-name> 4
```

### List vaults

If you don't know the vault name, you can generate a list like this:

```shell
python removeVault.py <region-name> LIST
```

### Inventory retrieval jobs

A vault inventory is necessary to remove all the archives inside of it.
By default, we will look for an existing inventory and use it.
If there is none, we will initiate a new one.

You can change this behavior using the `job_id` argument, with the following values:
- `LATEST` (default): use the latest inventory available, or initiate a new one if there is none
- `NEW`: force initiating a new inventory retrieval job
- `LIST`: list the inventory retrieval jobs availables
- `<job_id>`: give a specific job ID to use

For example to force a new inventory:

```shell
python removeVault.py <region-name> <vault-name> NEW
```

If you want to use 4 processes to remove the archives AND force a new inventory:

```shell
python removeVault.py <region-name> <vault-name> 4 NEW
```

### Debug

By default, only the INFO messages will be printed to console. You can add a third argument "DEBUG" to the removeVault.py script if you want to show all messages.

Example :

```shell
python removeVault.py <region-name> <vault-name> DEBUG
```

## Building the Docker image

If for whatever reason you don't want to use the [`leeroyb/glacier-vault-remove`](https://hub.docker.com/r/leeroyb/glacier-vault-remove) image on Docker Hub, you can also build the image yourself from this repository.

1. Make sure you have docker installed
2. Clone or download this repository
3. Build the image:

```
docker build -t glacier-vault-remove .
```

4. Create a `credentials.json` as described above

5. Run the tool in the docker container:

```
docker run -v /path/to/credentials.json:/app/credentials.json glacier-vault-remove <region> <vault|LIST> [DEBUG] [NUM_PROCESSES] [<job_id>|LIST|NEW|LATEST]
```

Make sure you use the _full_ absolute path to `credentials.json`, relative paths do not work here.

Licence
======================
(The MIT License)

Copyright (C) 2013 Leeroy Brun, www.leeroy.me

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

