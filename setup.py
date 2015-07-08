from setuptools import setup
from subprocess import call
import os

required = [
]

setup(name='pterraform',
      version='0.1.2',
      description='Terraform wrapper for Python',
      url='https://github.com/jrbudnack/pterraform',
      author='Jeremy Budnack',
      packages=[
        'pterraform'
      ],
      install_requires=required,
      include_package_data=True,
      zip_safe=False,
      data_files=[])
