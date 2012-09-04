from setuptools import setup, find_packages
setup(
    name = "BigSister",
    version = "0.1.1",
    packages = find_packages(),

    install_requires = ['requests',
                        'google-api-python-client']
)