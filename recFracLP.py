import numpy as np
import itertools
import math
import pickle
import os
from time import time
import multiprocessing as mp
from mip import Model, xsum, BINARY, MAXIMIZE, CONTINUOUS 

from LPGenSage import LPGenSage


#this codes generates the fractional rectangle cover LP
#the initFile.py must be ran first
q=2

generateAll=True
colsGenerate=[]
fileName='fileName'

Plane=LPGenSage(q)
if generateAll:
	columns=Plane.triple_classes
	print('Generating all colums LP...')
	#generates the weight files
else:
	columns=colsGenerate
	print('Generating the given columns')


for triple in columns:
	Plane.LP_build_triple(triple)

m=Plane.PlaneLP(columns)
m.write(fileName+'.lp')
print("The file {} has been created.".format(fileName+'.lp'))
