# Generic setop.py
from setuptools import setup, find_packages
setup(
name="Gloffis FEWS Configuration Scripts",
packages=(find_packages(exclude=('tests'))),
version='1.0.0',
description='',
long_description=open('readme.txt').read(),
author='B. van Osnabrugge, A. Onate, M. den Toom, J. Verkade',
author_email='bart.vanosnabrugge@deltares.nl',
download_url='https://repos.deltares.nl/repos/gloffis-prod/trunk/scripts/Python',
)