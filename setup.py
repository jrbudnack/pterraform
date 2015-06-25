from setuptools import setup
from subprocess import call
import os

required = [
        "python-keystoneclient==1.1.0",
]

setup(name='pterraform',
      version='0.1',
      description='Terraform wrapper for Python',
      url='',
      author='Jeremy Budnack',
      packages=[
        'pterraform'
      ],
      install_requires=required,
      include_package_data=True,
      zip_safe=False,
      data_files=[])
