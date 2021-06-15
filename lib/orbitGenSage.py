import numpy as np
import itertools
#import pandas as pd
import math
import pickle
import os
from time import time
import multiprocessing as mp
from autGenSage import autGenSage

class orbitGenSage(autGenSage):

	def __init__(self,*args,**kwargs):
		#First, we load the data:
		super(orbitGenSage,self).__init__(*args, **kwargs)
		self.pathFolder=os.path.join(os.getcwd(), 'Files_{}'.format(self.p))
		try:
			with open(os.path.join(self.pathFolder,'aut_table_{}.pickle'.format(self.p)), 'rb') as f:
				self.aut_table=pickle.load(f)
			with open(os.path.join(self.pathFolder,'aut_table_lines_{}.pickle'.format(self.p)), 'rb') as f:
				self.aut_table_lines=pickle.load(f)
		except OSError:
			print('The automorphisms files might not be generated yet. Running the autGenFile method...')
			self.autGenFile()
			with open(os.path.join(self.pathFolder,'aut_table_{}.pickle'.format(self.p)), 'rb') as f:
				self.aut_table=pickle.load(f)
			with open(os.path.join(self.pathFolder,'aut_table_lines_{}.pickle'.format(self.p)), 'rb') as f:
				self.aut_table_lines=pickle.load(f)


	###############LINE CLASSES#################
	def porbit(self,lines):
		'''
		This function computes the orbit of a set of lines. Lines should be a tuple, the output is a set with ordered tuples
		'''
		if len(set(lines))==1:
			return list(range(self.p**2+self.p+1))
		else:
			return [tuple(sorted(map(lambda val: aut[val], lines))) for aut in self.aut_table_lines]

	def porbit_set(self,lines):
		'''
		This function computes the orbit of a set of lines. Lines should be a tuple, the output is a set with ordered tuples
		Here, we avoid the sorting in order to speed up computation
		'''
		return list(set([frozenset(aut[line] for line in lines) for aut in self.aut_table_lines]))

	def porbit_triples(self,triple):
		'''
		This function computes the orbit of tripes (line,point, X)
		'''
		line=triple[0]
		point=triple[1]
		X=triple[2]
		orbit=[]
		for ind, aut in enumerate(self.aut_table_lines):
			autPoint=self.aut_table[ind][point]
			autLine=aut[line]
			autX=frozenset(aut[line] for line in X)
			orbit.append((autLine,autPoint,autX))
		
		return list(set(orbit))

	def line_stabilizer(self,lines):
		'''
		This function computes the stabilizer of a given set of lines. 
		'''
		stabilizer=[]
		for ind,aut in enumerate(self.aut_table_lines):
			image=frozenset([aut[line] for line in lines])
			if image==frozenset(lines):
				stabilizer.append(self.aut_table[ind])
		
		return stabilizer

	def line_point_orbits(self,points, stabilizer):
		"""
		This function computes the orbit of a set of points on a given stabilizer.
		"""
		return list(set([frozenset(aut[point] for point in points) for aut in stabilizer]))

#orbitGenSage(4)
