import numpy as np
import itertools
import math
import pickle
import os
from time import time
import multiprocessing as mp

from planeGenSage import planeGenSage
from autGenSage import autGenSage
from orbitGenSage import orbitGenSage
from classGenSage import classGenSage


#This code generates the files required for computation.
q=2

#generate automorphism files
print('Generating the automorphism files...')
autGenSage(q).autGenFile()

#generates the line orbits
print('Generating the line orbit files...')
classGenSage(q).lineClassFileGen()


#generates the valid triple orbits
print('Generating the valid triple orbits files...')
classGenSage(q).triplesFileGen_mp_v2()

print('Generating the (A,B) orbits files...')
#generates the (A,B) classes
classGenSage(q).AB_classesFileGen_mp()



