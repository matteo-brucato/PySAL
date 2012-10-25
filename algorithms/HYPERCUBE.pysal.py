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


def BIT(m, p): # Returns the p+1'th least significant bit of 'm', p>=0
	return (m >> p) & 1

def COMPLEMENTA(m, p):
	if BIT(m, p) == 0: return m + 2**p
	else:              return m - 2**p


class MyHypercube(Hypercube):
	
	########################################################################
	## SUMMATION ON HYPERCUBE
	########################################################################
	#;; SUM_HYPERCUBE
	def SUM_HYPERCUBE(self, propagate=False):
		k = self.k
		
		# Summation
		for d in reversed(range(k)):
			forall i as P where i in range(0, 2**d) do in parallel using d:
				P['b'] = P.getfrom('a', i + 2**d)
				P['a'] = P['a'] + P['b']
		
		# Propagation
		if not propagate: return
		for d in range(k):
			forall i as P where i in range(2**d, 2**(d+1)) do in parallel using d:
				P['b'] = P.getfrom('a', i - 2**d)
				P['a'] = P['b']
	#;;
	

	########################################################################
	## BITONIC-MERGESORT ON HYPERCUBE
	########################################################################
	#;; BITONIC_MERGESORT_HYPERCUBE
	def BITONIC_MERGESORT_HYPERCUBE(self):
		k = self.k
		n = 2**k
		
		# Do k=log(n) iterations 'i'
		for i in range(0, k):
			# For each iteration 'i' do i+1 passes 'j'
			for j in reversed(range(0, i+1)):
				d = 2**j     # <-- distance from neighbor to read data from
				forall h as P where h in range(0, n) do in parallel using i,d:
					if h % (2*d) < d:
						t = P.getfrom('a', h + d)
						if h % 2**(i+2) < 2**(i+1):
							P['b'] = max(P['a'], t)
							P['a'] = min(P['a'], t)
						else:
							P['b'] = min(P['a'], t)
							P['a'] = max(P['a'], t)
					else:
						P['a'] = P.getfrom('b', h - d, getnew=True)
	#;;
	

	########################################################################
	## MATRIX MULTIPLICATION ON HYPERCUBE
	########################################################################
	""" Note:
	Supponiamo di avere due matrici nxn da voler moltiplicare, ma non un n
	qualunque: n deve essere potenza di 2, ovvero n=2^h per un certo h.
	Usiamo un ipercubo di n^3 processori. Quindi k=log(n^3)=log(2^3h)=3h,
	quindi ogni processore è collegato a 3h altri processori, quindi la 
	rappresentazione binaria di ogni processore consta di 3h bit. E' quindi
	possibile dividere tali rappresentazioni binarie in 3 gruppi di h bit
	ciascuno, e chiamare ognuno di questi gruppi 'k','i' e 'j'.
	Ad esempio, se h=2 => 00|01|10 per il processore 000110 con k=00, i=01 e j=10.
	Una tripla (k,i,j) quindi rappresenta un processore dell'ipercubo.
	"""
	#;; MATRIX_MULTIPLICATION_HYPERCUBE
	def MATRIX_MULTIPLICATION_HYPERCUBE(self):
		k = self.k
		h = k//3
		
		# First phase: Distribution of data on the entire hypercube, in O(log n) time
		for p in range(2*h, 3*h): # Distribution of A's and B's along dimension 'k'
			forall m as P where m in range(2**p, 2**(p+1)) do in parallel using p:
				D = COMPLEMENTA(m, p)
				P['A'] = P.getfrom('A', D)
				P['B'] = P.getfrom('B', D)
		
		for p in reversed(range(0,h)): # Distribution of A's along dimension 'j'
			forall m as P where m in range(0, 2**(3*h)) if BIT(m,p) != BIT(m,2*h+p) do in parallel using p:
				D = COMPLEMENTA(m, p)
				P['A'] = P.getfrom('A', D)
		
		for p in reversed(range(h, 2*h)): # Distribution of B's along dimension 'i'
			forall m as P where m in range(0, 2**(3*h)) if BIT(m,p) != BIT(m,h+p) do in parallel using p:
				D = COMPLEMENTA(m, p)
				P['B'] = P.getfrom('B', D)
		
		# Second phase: Multiplications in O(1) time
		forall m as P where m in range(0, 2**(3*h)) do in parallel:
			P['C'] = P['A'] * P['B']
		
		# Third phase: Summations in O(log n) time
		for p in range(2*h, 3*h):
			forall m as P where m in range(0, 2**(3*h)) do in parallel using p:
				D = COMPLEMENTA(m, p)
				E = P.getfrom('C', D)
				P['C'] = P['C'] + E
	#;;
	


########################################################################
############################### TESTS ##################################
########################################################################
if __name__ == '__main__':
	########################################################################
	## Testing SUMMATION ON HYPERCUBE
	########################################################################
	h = MyHypercube(4)
	h.randomfeed(0,3)
	correctsum = sum([ h.M[i]['a'] for i in range(len(h.M)) ])
	#h.feed('a', [5,6,3,13,7,10,9,2])
	print ("\nTesting Summation on", h.str_variable('a'))
	print ('Executing SUM_HYPERCUBE...')
	h.SUM_HYPERCUBE(True)
	print ('Resulting', h.str_variable('a'))
	assert(h.M[0]['a'] == correctsum)


	########################################################################
	## Testing BITONIC MERGESORT ON HYPERCUBE
	########################################################################
	h = MyHypercube(4)
	h.randomfeed(-20,20)
	correctorder = sorted([ h.M[i]['a'] for i in range(len(h.M)) ])
	print ("\nTesting Bitonic Mergesort on", h.str_variable('a'))
	print ('Executing BITONIC_MERGESORT_HYPERCUBE...')
	h.BITONIC_MERGESORT_HYPERCUBE()
	# h.M.sort(key=lambda p: p.a)   # <-- Python's sorting is far faster!!
	print ('Resulting', h.str_variable('a'))
	assert([ h.M[i]['a'] for i in range(len(h.M)) ] == correctorder)


	########################################################################
	## Testing MATRIX MULTIPLICATION ON HYPERCUBE
	########################################################################
	from numpy import matrix
	from math import log
	# Example extracted from the book
	a = (
			(1, 2), 
			(3, 4),
	)
	b = (
			(-5,-6),
			( 7, 8),
	)
	assert len(a) == len(b)
	#correctproduct = [ 9, 10, 13, 14 ]
	correctproduct = (matrix(a) * matrix(b)).flatten().tolist()[0]
	# Create the hypercube
	n = len(a)
	h = MyHypercube(3*int(log(n,2)))	# In this case, the hypercube range will be 3
	# Feed the hypercube
	for i in range(n):
		for j in range(n):
			h.M[n*i+j]['A'] = a[i][j]
			h.M[n*i+j]['B'] = b[i][j]
	print ("\nTesting Matrix Multiplication on", h)
	print ('Executing MATRIX_MULTIPLICATION_HYPERCUBE...')
	h.MATRIX_MULTIPLICATION_HYPERCUBE()
	print ('Resulting', h.str_variable('C'))
	assert([ h.M[i]['C'] for i in range(n*n) ] == correctproduct)

	# My example
	a = (
			(2, 5, 6, 1),
			(0, 7, 8, 3),
			(4, 0, 1, 0),
			(1, 1, 1, 1),
	)
	b = (
			(-9,-8,-7,-3),
			(-6,-5,-4,-1),
			(-2, 0,-1, 0),
			(-1, 0, 0, 0),
	)
	assert len(a) == len(b)
	#correctproduct = [ -61,  -41,  -40,  -11, -61,  -35,  -36,   -7, -38,  -32,  -29,  -12, -18,  -13,  -12, -4 ]
	correctproduct = (matrix(a) * matrix(b)).flatten().tolist()[0]
	# Create the hypercube
	n = len(a)
	h = MyHypercube(3*int(log(n,2)))	# In this case, the hypercube range will be 6
	# Feed the hypercube
	#h.randomfeed(0,0,vars=['A','B','C'])
	for i in range(n):
		for j in range(n):
			h.M[n*i+j]['A'] = a[i][j]
			h.M[n*i+j]['B'] = b[i][j]
	print ("\nTesting Matrix Multiplication on", h)
	print ('Executing MATRIX_MULTIPLICATION_HYPERCUBE...')
	h.MATRIX_MULTIPLICATION_HYPERCUBE()
	print ('Resulting', h.str_variable('C'))
	assert([ h.M[i]['C'] for i in range(n*n) ] == correctproduct)

	print ("\nAll tests passed successfully!")
