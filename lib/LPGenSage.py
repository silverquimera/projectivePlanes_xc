import numpy as np
import itertools
#import pandas as pd
import math
import pickle
import os
from time import time
import multiprocessing as mp
from mip import Model, xsum, BINARY, CONTINUOUS 
import tqdm
from collections import Counter
from classGenSage import classGenSage

class LPGenSage(classGenSage):
	def __init__(self,*args,**kwargs):
		#First, we load the data:
		super(LPGenSage,self).__init__(*args, **kwargs)

		############ Load line classes ######################### 
		

		self.line_classes=[]
		for classSize in range(1,self.n):
			# try: 
			with open(os.path.join(self.pathFolder,'class_{}_{}.pickle'.format(self.p,classSize)), 'rb') as f:
				self.line_classes+=pickle.load(f)
			#print("Line class {} loaded".format(classSize))
			# except OSError:
			# 	print("Line classes have not been generated. Starting class generator:")
			# 	self.lineClassFileGen()
			# 	with open(os.path.join(self.pathFolder,'class_{}_{}.pickle'.format(self.p,classSize)), 'rb') as f:
			# 		self.line_classes+=pickle.load(f)
			# 	print("Line class {} loaded".format(classSize))

		############ Load triple classes ######################
		self.triple_classes=[]
		self.triples_dict=dict()
		for tripleSize in range(1,self.p**2+self.p+1):
			# try:
			with open(os.path.join(self.pathFolder,'triples_{}_{}.pickle'.format(self.p,tripleSize)), 'rb') as f:
				self.triples_dict[tripleSize]=pickle.load(f)
				self.triple_classes+=self.triples_dict[tripleSize]
		print("Triple classes (variables) loaded. Total number of variables is {}".format(len(self.triple_classes)))
			# except OSError:
			# 	print('Triples have not been generated')
			# 	self.triplesFileGen_mp_v2()
			# 	with open(os.path.join(self.pathFolder,'triples_{}_{}.pickle'.format(self.p,tripleSize)), 'rb') as f:
			# 		self.triples_dict[tripleSize]=pickle.load(f)
			# 		self.triple_classes+=self.triples_dict[tripleSize]
			# 	print('Triple classes created')

		# ############## Load AB classes #######################
		# try:
		# for classSize in range(1,self.n):
		# 	# try: 
		# 	with open(os.path.join(self.pathFolder,'ABclass_{}_{}.pickle'.format(self.p,classSize)), 'rb') as f:
		# 		self.AB_classes+=pickle.load(f)
		# 	print("AB class {} loaded".format(classSize))
		
		# self.AB_classes_cleaned=[(A,B) for (A,B) in tqdm.tqdm(self.AB_classes) if all(len(set(self.dict_lines[line]).intersection(set(B)))>0 for line in A)>0]
		# print("AB classes are cleaned, the total size is", len(self.AB_classes_cleaned))
		AB_classesPath=os.path.join(self.pathFolder,'AB_classes_{}.pickle'.format(self.p))
		with open(AB_classesPath, 'rb') as f:
			self.AB_classes=pickle.load(f) 
			print("AB_classes loaded. Total is ", len(self.AB_classes))

		
		# 	print('AB_classes loaded.')
		# except OSError:
		# 	print("AB classes not generated. Starting generating script.")
		# 	self.AB_classesFileGen_mp()
		# 	with open(os.path.join(self.pathFolder,'ABclasses_{}.pickle'.format(self.p)), 'rb') as f:
		# 		self.AB_classes=pickle.load(f)
		# 	print('AB_classes loaded.')


	def triple_orbits_fileGen_aux(self,triple):
		print("Computing the orbit of: ", triple)
		orbit=self.porbit_triples(triple)
		print("Orbit Computed, ", triple)
		orbitPath=os.path.join(self.pathFolder,'tripleOrbits','orbit_{}.pickle'.format(triple))
		with open(orbitPath, 'wb') as f:
			pickle.dump(orbit, f)
		print("Orbit {} file saved.".format(triple))

	def triple_orbits_fileGen(self):
		pool = mp.Pool(mp.cpu_count())	
		results = pool.map(self.triple_orbits_fileGen_aux, [triple for triple in tqdm.tqdm(self.triple_classes)])
		pool.close()


	
	def triple_finder(self, triple):
		"""
		Given a triple (line,point, X) this method finds the class respresentative.
		"""
		line=triple[0]
		point=triple[1]
		X=frozenset(triple[2])
		if (point in self.dict_lines[line]) and (point in self.points_in_lines(X)) and (line not in X):
			possible_triples=[newTriple for newTriple in self.triple_classes if len(newTriple[2])==len(X)]
			for newTriple in possible_triples:
				if (line,point,X) in self.porbit_triples(newTriple):
					return newTriple
		else:
			#raise print("Not a valid triple")
			print("Not a valid triple")
	
	def AB_class_constraint(self,ABclass):
		A=ABclass[0]
		B=ABclass[1]
		print("Starting computation for ABclass {}".format(ABclass))
		weights={ABclass: dict()}
		counter=0
		for triple in self.triple_classes:
			counter+=1
			print(ABclass,counter/len(self.triple_classes),"%")
			orbit=self.porbit_triples(triple)
			for (line,point, X) in orbit:
				if line in A:
					if point in B:
						if frozenset(A).intersection(X)==frozenset():
							if frozenset(B).issubset(self.points_in_lines(X)):
								if triple in weights[ABclass].keys():
									weights[ABclass][triple]+=1
								else:
									weights[ABclass][triple]=1
		print("The class {} is done".format(ABclass))
		return weights

	def LP_weights(self):

		print("Constructing the LP. This might take some time.")
		pool = mp.Pool(mp.cpu_count())	
		results = pool.map(self.AB_class_constraint, self.AB_classes)
		pool.close()

		LP_weights=dict()
		for result in results:
			LP_weights.update(result)
		
		LPpath=os.path.join(self.pathFolder,'LP_weights_{}.pickle'.format(self.p))
		with open(LPpath, 'wb') as f:
			pickle.dump(LP_weights, f) 

		return LP_weights

	def LPGen(self):
		try:
			with open(os.path.join(self.pathFolder,'LP_weights_{}.pickle'.format(self.p)), 'rb') as f:
				LP_weights=pickle.load(f)
		except OSError:
			LP_weights=self.LP_weights()


		#Define the model
		m=Model(sense='MAX')
		#Create Variables:
		y={key:m.add_var(name='y_{}'.format(key), var_type=CONTINUOUS, lb=0,ub=1) for key in self.triple_classes}

		for (A,B) in LP_weights.keys():
			m.add_constr(xsum(LP_weights[(A,B)][key]*y[key] for key in LP_weights[(A,B)].keys())<=1, str([A,B]))

		m.objective=xsum(LP_weights[self.AB_classes[0]][key]*y[key] for key in LP_weights[self.AB_classes[0]].keys())

		return m

	def LPGen_cplx(self):
		try:
			with open(os.path.join(self.pathFolder,'LP_weights_{}.pickle'.format(self.p)), 'rb') as f:
				LP_weights=pickle.load(f)
		except OSError:
			LP_weights=self.LP_weights()

		m=cpx.Model(name="LPGen Model")
		y={key:m.continuous_var(name='y_{}'.format(key), lb=0,ub=1) for key in self.triple_classes}
		for (A,B) in LP_weights.keys():
			m.add_constraint(
				ct=m.sum(LP_weights[(A,B)][key]*y[key] for key in LP_weights[(A,B)].keys())<=1, ctname=str([A,B])
				)
		objective=m.sum(LP_weights[self.AB_classes[0]][key]*y[key] for key in LP_weights[self.AB_classes[0]].keys())
		m.maximize(objective)


		m.solve()

		for key in y:
			if y[key].solution_value>0:
				print(key, "value: ", y[key].solution_value)


	def LP_build_triple_aux(self, tripleInput):
		
		
		A=tripleInput[0]
		B=tripleInput[1]
		triple=tripleInput[2]
		orbit=tripleInput[3]

		#print(A,B)

		counter=0
		for (line,point, X) in orbit:
			if line in A:
				if point in B:
					if frozenset(A).intersection(X)==frozenset():
						if frozenset(B).issubset(self.points_in_lines(X)):
							counter+=1
		if counter>0:
			print((A,B,triple,counter), " was added.")
			return (A,B,triple,counter)

	def LP_build_abClass_aux(self, tripleInput):
		
		
		A=tripleInput[0]
		B=tripleInput[1]
		triple=tripleInput[2]
		orbit=self.porbit_triples(tripleInput[2])

		#print(A,B)

		counter=0
		for (line,point, X) in orbit:
			if line in A:
				if point in B:
					if frozenset(A).intersection(X)==frozenset():
						if frozenset(B).issubset(self.points_in_lines(X)):
							counter+=1
		if counter>0:
			print((A,B,triple,counter), " was added.")
			return (A,B,triple,counter)


	def LP_build_triple(self, triple):
		print("Computing the column ", triple)
		orbit=self.porbit_triples(triple)
		self.counterTool=0
		pool = mp.Pool(mp.cpu_count())	
		results = pool.map(self.LP_build_triple_aux, [(ABclass[0],ABclass[1],triple,orbit) for ABclass in tqdm.tqdm(self.AB_classes)])
		pool.close()
		results=[result for result in results if result!=None]

		LPpath=os.path.join(self.pathFolder,'LP_weights_{}.pickle'.format(triple))
		with open(LPpath, 'wb') as f:
			pickle.dump(results, f) 

		return results

	def LP_build_abClass(self, abClass):
		print("Computing the AB_class {} constraint ".format(abClass))
		pool = mp.Pool(mp.cpu_count())	
		results = pool.map(self.LP_build_abClass_aux, [(abClass[0],abClass[1],tripleClass) for tripleClass in tqdm.tqdm(self.triple_classes)])
		pool.close()
		results=[result for result in results if result!=None]

		LPpath=os.path.join(self.pathFolder,'LP_weights_AB_{}.pickle'.format(abClass))
		with open(LPpath, 'wb') as f:
			pickle.dump(results, f) 

		return results





Plane=LPGenSage(4)
triples=[Plane.triple_classes[i] for i in [1514,1515,1516]]
for triple in triples:
	weights=Plane.LP_build_triple(triple)
	# maxval=0
	# for weight in weights:
	# 	val=weight[3]
	# 	if len(weight[0])==1 and len(weight[1])==1:
	# 		val1=val
	# 	if val>=maxval:
	# 		maxval=val
	# 		maxweight=weight
	# print(triple)
	# print(maxweight)
	# print(val1/maxval)    
	# print("--------------")


# lpWeightsPath='./LP_weights_support/'

	

# Plane=LPGenSage(4)



# tic=time()
# Plane.triple_orbits_fileGen()
# # Plane.LP_build_abClass(Plane.AB_classes[0])
# print("Total time to compute this colum (sec):", time()-tic)


# tic=time()
# Plane.LP_build_triple(Plane.triple_classes[11])  
# print("Total time to compute this colum (sec):", time()-tic)
#for i in range(len(Plane.triple_classes)-1000, len(Plane.triple_classes)-750):
#		Plane.LP_build_triple(Plane.triple_classes[i])
#Plane=LPGenSage(3)
#print([Plane.triple_classes[i] for i in [5]])
#print(Plane.dict_lines)
#m=LPGenSage(3).LPGen()
#m.write('Plane3LPv2.lp')
#status=m.optimize()
#print(status)
#print(m.objective_value)

#for v in m.vars:
#    if v.x>0:
#        print(v.name, v.x)
# Plane=LPGenSage(3)
# for tripleClass in Plane.triple_classes:
# 	Plane.LP_build_triple(tripleClass)