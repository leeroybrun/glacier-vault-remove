amazon-glacier-removal
======================

Tool to remove all archives stored inside an Amazon Glacier vault. It will then remove the vault too.

This requires boto, you can install it like this :

```shell
pip install boto
```

Then create a `credentials.json` file in the script directory :

```json
{
	"AWSAccessKeyId": "YOURACCESSKEY",
	"AWSSecretKey":   "YOURSECRETKEY"
}
```

You can then use the script like this :

```shell
python .\removeVault.py REGION-NAME VAULT-NAME
```

Example :

```shell
python .\removeVault.py eu-west-1 my_vault
```