import numpy as np
import itertools
import math
import pickle
from time import time
import multiprocessing as mp
from planeGenSage import planeGenSage
import os


class autGenSage(planeGenSage):
	#First, let us compute all triples of non-colinear points:

	def point_translation(self, old_dict):
		'''
		Given a dict of triples of points in the plane, this transforms it into index like format
		'''
		return {self.index_dict[key]:self.index_dict[old_dict[key]] for key in old_dict.keys()}


	def paut(self):
		auts=[self.point_translation(aut.dict()) for aut in self.Plane.automorphism_group()]
		return auts

	def point_to_line_aut(self,aut):
		"""
		Given an automorphism of points, this code returns the automorphism of lines.
		"""
		return {line:self.lines_dict[tuple(sorted(aut[point] for point in self.dict_lines[line]))] for line in self.dict_lines}

	def line_to_point_aut(self,aut_line):
		"""
		Given an automorphism of lines, this code returns the automorphism of points.
		"""
		return {point: self.dict_pp[tuple(sorted(aut_line[line] for line in self.pp_dict[point]))] for point in self.pp_dict}

	#Next, we save the automorphisms. This code takes a while to run:
	def autGenFile(self):
		currentFolder=os.getcwd()
		try:
			#Create directories
			pathDestination=os.path.join(currentFolder, 'Files_{}'.format(self.p))	
			if not os.path.isdir(pathDestination):
				print('The main directory does not exists, creating the directory.')
				os.mkdir(pathDestination)

			#Create the automorphisms table
			aut_table=self.paut()

			#Then, we save the file into a pickle
			autTablePath=os.path.join(pathDestination,'aut_table_{}.pickle'.format(self.p))
			with open(autTablePath, 'wb') as f:
				pickle.dump(aut_table, f)
			
			aut_table_lines=[self.point_to_line_aut(aut) for aut in aut_table]
			autTableLinesPath=os.path.join(pathDestination,'aut_table_lines_{}.pickle'.format(self.p))
			with open(autTableLinesPath, 'wb') as f:
				pickle.dump(aut_table_lines, f)
		except OSError:
			print("An OS ocurred in the creation of the files.")

				
				

#autGenSage(4).autGenFile()