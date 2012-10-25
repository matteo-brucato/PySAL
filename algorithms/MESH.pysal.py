#coding=utf-8
"""
PySAL - Python Synchronous Algorithm Library
------------------------------------------------------------------------
Copyright (C) 2012  Matteo Brucato  <mattfeel@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
from synchronous_unshared import *


class MyMesh(Mesh):
	
	########################################################################
	## SUMMATION ON MESH
	########################################################################
	#;; SUM_MESH
	def SUM_MESH(self, propagate=False):
		n = self.n
		
		# Parallel vertical sums
		for i in reversed(range(n-1)):
			forall (i,j) as P where j in range(0,n) do in parallel:
				b = P.getfrom('a', i+1, j)
				P['a'] = P['a'] + b
		
		# Sequentially sum row 0
		for j in reversed(range(n-1)):
			P = self.getproc(0,j)
			a = P.getfrom('a', 0, j+1)
			P['a'] = P['a'] + a
		
		# Propagation
		if not propagate: return
		for j in range(1,n):
			P = self.getproc(0,j)
			a = P.getfrom('a', 0, j-1)
			P['a'] = a
		for i in range(1,n):
			forall (i,j) as P where j in range(0,n) do in parallel:
				b = P.getfrom('a', i-1, j)
				P['a'] = b
	#;;
	

	########################################################################
	## MATRIX MULTIPLICATION ON CYCLIC MESH
	########################################################################
	#;; MATRIX_MULTIPLICATION_CYCLIC_MESH
	def MATRIX_MULTIPLICATION_CYCLIC_MESH(self):
		n = self.n
		
		# Positioning of all elements
		for p in range(0, n-1):
			forall (i,j) as P where i in range(0, n) where j in range(0, n) do in parallel using p,n:
				if i > p: P['a'] = P.getfrom('a', i, (j+1)%n)
				if j > p: P['b'] = P.getfrom('b', (i+1)%n, j)
		
		# Set all c's to zero
		forall (i,j) as P where i in range(0, n) where j in range(0, n) do in parallel:
			P['c'] = 0
		
		# Compute actual matrix multiplication
		for q in range(0, n):
			forall (i,j) as P where i in range(0, n) where j in range(0, n) do in parallel using n:
				P['c'] = P['c'] + P['a'] * P['b']
				P['a'] = P.getfrom('a', i, (j+1)%n)
				P['b'] = P.getfrom('b', (i+1)%n, j)
	#;;
	


########################################################################
############################### TESTS ##################################
########################################################################
if __name__ == '__main__':
	########################################################################
	## Testing SUMMATION ON MESH
	########################################################################
	m = MyMesh(3)
	m.randomfeed(-5, 5, ['a'])
	correctsum = sum([ m.M[i]['a'] for i in range(len(m.M)) ])
	print ("\nTesting Summation on", m)
	print ("Executing SUM_MESH...")
	m.SUM_MESH(True)
	print ("Resulting", m)
	assert(m.M[0]['a'] == correctsum)


	########################################################################
	## Testing MATRIX MULTIPLICATION ON CYCLIC MESH
	########################################################################
	m = MyMesh(3, cyclic=True)
	a = (2,5,6,1,0,7,8,3,4)
	for i,r in enumerate(m.M):
		m.M[i]['a'] = a[i]
	b = (-9,-8,-7,-3,-6,-5,-4,-1,-2)
	for i,r in enumerate(m.M):
		m.M[i]['b'] = b[i]
	correctproduct = [ -57,  -52,  -51, -37,  -15,  -21, -97,  -86,  -79 ]
	print ("\nTesting Matrix Multiplication on", m)
	print ("Executing MATRIX_MULTIPLICATION_CYCLIC_MESH...")
	m.MATRIX_MULTIPLICATION_CYCLIC_MESH()
	print ("Resulting", m)
	assert([ m.M[i]['c'] for i in range(len(m.M)) ] == correctproduct)

	print ("\nAll tests passed successfully!")
