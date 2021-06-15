import numpy as np
import itertools
import math
import pickle
from time import time
import multiprocessing as mp

import sage.all
from sage.combinat.designs.block_design import DesarguesianProjectivePlaneDesign as PlaneDesign

class planeGenSage(object):
	'''
	This code creates a class with 
	'''
	def __init__(self, p):
		self.p = p
		self.n=self.p**2+self.p+1
		self.Plane=PlaneDesign(p)
		self.index_dict=self.Plane._point_to_index
		self.main_dict=self.Plane.incidence_graph().to_dictionary()
		self.dict_lines = {line:tuple(sorted([self.Plane._point_to_index[point] for point in block])) for (line,block) in enumerate(self.Plane.blocks())}
		self.lines_dict={item:key for (key,item) in self.dict_lines.items()}
		self.pp_dict ={point: tuple(sorted(line for line in self.dict_lines.keys() if point in self.dict_lines[line])) for point in range(self.n)}
		self.dict_pp={val:key for (key,val) in self.pp_dict.items()}
	###############################################################
	# METHODS
	###############################################################
	
	###Some other general methods for lines/points incidences
	def incidences_between(self,A,B):
		"""
		Given a set of lines A and a set of points B, this function computes the number of times a line
		in A passses through a point in B i.e. |E[A:B]| 
		"""	
		
		points=tuple()
		for line in A:
			points+=self.dict_lines[line]
		return len([point for point in points if point in B])
	
	def points_in_lines(self,A):
		"""
		Given a set of lines A, we compute the set of points in these lines
		"""
		setPoints=tuple()
		for line in A:
			setPoints+=self.dict_lines[line]
			
		return set(setPoints)


