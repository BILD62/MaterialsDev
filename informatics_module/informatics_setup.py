'''
#Install required packages with the pip command 
- to look for the the package in PyPI,
- and install everything in your environment to ensure that requests will work.
to get help with the package you can run 'pip -h'
'''

# Need to run these in notebook directly
#! pip install xmljson 
# ! pip install nltk # Already in DataHub
# ! pip install xmltodict
# ! pip install Biopython

import sys
import getopt # Not used in notebook
import requests # Not used in notebook
import json

from Bio import Entrez

import nltk
from nltk import word_tokenize
from nltk import Tree

from itertools import product

import urllib
import urllib.request 
import urllib.error
import urllib.parse

import pandas as pd
 
import random