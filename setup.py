from setuptools import setup, find_packages
import json
setup(
    name = "GlacierVaultRemove",
    version = "0.1",
    packages = find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['3>=1.4.4'],

    # metadata for upload to PyPI
    author = "Leeroy Brun",
    author_email = "leeroy.brun@gmail.com",
    description = "Tool used to remove all archives stored inside an Amazon Glacier vault.",
    license = "MIT",
    keywords = "aws amazon glacier boto archives vaults",
    url = "https://github.com/leeroybrun/glacier-vault-remove",
)

with open("credentials.json", "w") as outfile:
    json.dump({'AWSAccessKeyId': '<key>', 'AWSSecretKey': '<secretkey>'}, outfile, indent=4)
