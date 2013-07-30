from setuptools import setup, find_packages
setup(
    name = "GlacierVaultRemove",
    version = "0.1",
    packages = find_packages(),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['boto>=2.9.9'],

    # metadata for upload to PyPI
    author = "Leeroy Brun",
    author_email = "leeroy.brun@gmail.com",
    description = "Tool used to remove all archives stored inside an Amazon Glacier vault.",
    license = "MIT",
    keywords = "aws amazon glacier boto archives vaults",
    url = "https://github.com/leeroybrun/glacier-vault-remove", 
)