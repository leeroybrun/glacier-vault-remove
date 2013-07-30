glacier-vault-remove
======================

This tool can help you remove an Amazon Glacier vault, even if it is not empty.

It will remove all archives contained inside the vault, and then remove the vault itself.

It is intended to work well with vaults containing a lot of archives. I developed it because my vault contained more than 500'000 archives, and all other softwares crashed when I tried to remove all of them.

## Install

You can install the dependencies (boto) by calling the install script :

```shell
python setup.py install
```

## Configure

Then create a `credentials.json` file in the script directory :

```json
{
	"AWSAccessKeyId": "YOURACCESSKEY",
	"AWSSecretKey":   "YOURSECRETKEY"
}
```

## Use

You can then use the script like this :

```shell
python .\removeVault.py REGION-NAME VAULT-NAME
```

Example :

```shell
python .\removeVault.py eu-west-1 my_vault
```

Licence
======================
(The MIT License)

Copyright (C) 2013 Leeroy Brun, www.leeroy.me

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
