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
from synchronous_shared import *
from copy import *
from operator import *
import math, random, sys, functools
sys.setrecursionlimit(sys.getrecursionlimit()**2)

"""
NOTE: All algorithms in this file are EREW, unless differently stated (like
in the case of the first version of the Tournament Sorting, which is CREW).

In fondo, esempi completi e funzionanti per la creazione di una PRAM e la 
sua esecuzione.

I vettori che si vogliono usare all'interno della PRAM vanno passati
al costruttore della PRAM dentro un dizionario.
* Esempio:
pram = PRAM({ 'a': [1,2,3,4], 'b': [ 0 for i in range(10) ] })

Quando si chiamano le funzioni implementate, solitamente, per come sono
state implementate, si passa loro un riferimento al vettore contenuto
nella PRAM, su cui si vuole fare il calcolo. Per recuperare tale riferimento
dalla PRAM già creata, usare la sintassi per i dizionari (es. pram['a']
per recuperare il vettore di nome 'a' dentro la PRAM pram).
Ovviamente è solo per comodità, in quanto ad ogni funzione viene sempre
passata l'intera PRAM, e i vettori necessari possono essere recuperati
all'interno delle funzioni implementate. L'unico motivo per cui non è stato
fatto così, è per mantenere le funzioni simili a quelle del libro.

Inoltre, è bene notare che tutte le funzioni di sommatoria e somme prefisse
utilizzano un vettore lungo il doppio del necessario, perché viene utilizzato
come heap. Quando si crea la PRAM per tali funzionalità, bisogna passargli
un vettore della dimensione giusta, nel quale gli elementi da sommare si
troviano nella seconda metà.

Il torneo al suo interno usa la Sommatoria, quindi esso prepara preventivamente 
un vettore in stile heap, per eseguire le sommatorie necessarie.

Negli esempi in basso, i vettori sono stati creati con un elemento in più
del necessario, per permettere indicizzazioni a partire da 1 (come nel libro).
Quindi, tutti gli eventuali output conterranno un primo elemento `None'.
"""


class MyPRAM(PRAM):
	########################################################################
	## SUMMATION ON PRAM - O(n) processors
	########################################################################
	#;; SUM_PRAM
	def SUM_PRAM(self, a, n):
		logn = int(math.log(n,2))
		
		# Ascending from last node level (not the leaves) to the root of the heap
		for k in reversed(range(logn)):
			forall i where i in range(2**k, 2**(k+1)) do in parallel using a:
				a[i] = a[2*i] + a[2*i+1]
		
		# The result is stored at the root of the heap
		return a[1]
	#;;


	########################################################################
	## SUMMATION ON PRAM - OPTIMAL - O(n/logn) processors
	## IMPORTANT!: It's assumed that both n and n/logn are powers of 2!
	########################################################################
	#;; SUM_PRAM_OPT
	def SUM_PRAM_OPT(self, a, n):
		logn = int(math.log(n,2))
		
		# Sequential sums: n/logn groups of logn elements each go in parallel
		forall i where i in range(n, 2*n, logn) do in parallel using a,n,logn:
			for j in range(i, i+logn):
				if j < 2*n:
					a[i//logn] += a[j]
		
		# Now it's like we have n/logn elements to sum up!
		log_n_over_logn = int(math.log(n/logn,2))
		
		# Ascending from last node level (not the leaves) to the root of the heap
		for k in reversed(range(log_n_over_logn)):
			forall i where i in range(2**k, 2**(k+1)) do in parallel using a:
				a[i] = a[2*i] + a[2*i+1]
		
		# The result is stored at the root of the heap
		return a[1]
	#;;
	

	########################################################################
	## ASSOCIATIVE OPERATION ON PRAM - O(n) processors
	## The summation exectues the '+' operation over all elements of a vector
	## kept in the PRAM. In the same way, it is possibile to execute any other
	## associative operation (e.g. multiplication, max, min, xor, GCD, LCM, ...)
	########################################################################
	#;; ASSOCIATIVE_OP_PRAM
	def ASSOCIATIVE_OP_PRAM(self, a, n, op):
		logn = int(math.log(n,2))
		
		# Ascending from last node level (not the leaves) to the root of the heap
		for k in reversed(range(logn)):
			forall i where i in range(2**k, 2**(k+1)) do in parallel using a,op:
				a[i] = op(a[2*i], a[2*i+1])
		
		# The result is stored at the root of the heap
		return a[1]
	#;;
	
	
	## TODO: ASSOCIATIVE OPERATION ON PRAM - OPTIMUM - O(n/logn) processors


	########################################################################
	## PREXIX SUM ON PRAM - O(n) processors
	########################################################################
	#;; PREFIX_SUM_PRAM
	def PREFIX_SUM_PRAM(self, a, b, n):
		logn = int(math.log(n,2))
		
		# Set the root with the summation of 'a'
		b[1] = self.SUM_PRAM(a, n)
		
		# Execute prefix sum in O(log n), using O(n) processors
		for k in range(1, logn+1):
			forall i where i in range(2**k, 2**(k+1)) do in parallel using a,b:
				if i%2==1: # right child
					b[i] = b[i//2]
				else:      # left child
					b[i] = b[i//2] - a[i+1]
	#;;
	
	
	## TODO: PREXIX SUM ON PRAM - OPTIMUM - O(n/logn) processors


	########################################################################
	## TOURNAMENT SORTING - CREW - O(n^2) processors
	## Note: Assuming n power of 2. It's possible to make a small change
	## to get rid of this assumption: we should pass to 'proc_tournament_sum'
	## longer columns of 'V', padded with extra zero's at the end.
	########################################################################
	#;; TOURNAMENT_SORT_CREW
	def TOURNAMENT_SORT_CREW(self, a, n):
		self['V'] = [ [ None for i in range(0, n+1) ] for i in range(0, n+1) ] # Matrix for 1s and 0s
		self['S'] = [ None for i in range(0, n+1) ]                            # Vector for column summations
		V = self['V'] # Renaming, just for syntactic simplicity
		S = self['S'] # Renaming, just for syntactic simplicity
		
		# Perform the tournament in O(1)
		forall (i,j) where i in range(1, n+1) where j in range(1, n+1) do in parallel using a,V:
			V[i][j] = 1 if a[i] <= a[j] else 0
		
		# Perform summations over columns in O(logn)
		forall i where i in range(1, n+1) do in parallel using V,n,S:
			# Prepare PRAM for summation
			csum = [ None for k in range(0, 2*n) ]
			for k in range(1, n):   csum[k] = 0
			for k in range(n, 2*n): csum[k] = V[k-n+1][i] # <-- copy i'th column of V
			self['subsum'] = csum
			
			# Execute summation of column
			S[i] = self.SUM_PRAM(self['subsum'], n)
		
		# Place every number in the right position in O(1)
		forall i where i in range(1, n+1) do in parallel using a,S:
			a[S[i]] = a[i]
		
		return a
	#;;
	
	########################################################################
	## REPLICATE - P=O(n)
	## Note: Assuming n power of 2.
	########################################################################
	#;; REPLICATE
	def REPLICATE(self, cpy, d, n):
		logn = int(math.log(n,2))
		
		cpy[1] = d
		for k in range(0, logn):
			forall i where i in range(1, 2**k+1) do in parallel using k,cpy:
				cpy[i+2**k] = cpy[i]
	#;;
	
	
	## TODO: REPLICATE_OPT - P=O(n/logn)
	
	
	########################################################################
	## TOURNAMENT SORTING - EREW (with REPLICATE) - O(n^2) processors
	## Note: Assuming n power of 2.
	########################################################################
	#;; TOURNAMENT_SORT_EREW
	def TOURNAMENT_SORT_EREW(self, a, n):
		self['V'] = [ [ None for i in range(0, n+1) ] for i in range(0, n+1) ] # Matrix for 1s and 0s
		self['R'] = [ [ None for i in range(0, n+1) ] for i in range(0, n+1) ] # Matrix for row-wise replicas
		self['C'] = [ [ None for i in range(0, n+1) ] for i in range(0, n+1) ] # Matrix for column-wise replicas
		self['S'] = [ None for i in range(0, n+1) ]                            # Vector for columns summations
		V = self['V'] # Renaming, just for syntactic similicity
		R = self['R'] # Renaming, just for syntactic similicity
		C = self['C'] # Renaming, just for syntactic similicity
		S = self['S'] # Renaming, just for syntactic similicity
		
		# Replication phase: copy each element of 'a' into a row of the matrix R and C
		forall i where i in range(1, n+1) do in parallel using a,n,R,C:
			self.REPLICATE(R[i], a[i], n)
			self.REPLICATE(C[i], a[i], n)
		
		# Perform the tournament in O(1)
		forall (i,j) where i in range(1, n+1) where j in range(1, n+1) do in parallel using a,V,R,C:
			V[i][j] = 1 if R[i][j] <= C[j][i] else 0
		
		# Perform summations over columns in O(logn)
		forall i where i in range(1, n+1) do in parallel using V,n,S:
			# Prepare PRAM for summation
			csum = [ None for k in range(0, 2*n) ]
			for k in range(1, n):   csum[k] = 0
			for k in range(n, 2*n): csum[k] = V[k-n+1][i] # <-- copy i'th column of V
			self['subsum'] = csum
			
			# Execute summation of column
			S[i] = self.SUM_PRAM(self['subsum'], n)
		
		# Place every number in the right position in O(1)
		forall i where i in range(1, n+1) do in parallel using a,S:
			a[S[i]] = a[i]
		
		return a
	#;;
	
	
	## TODO: TOURNAMENT_SORT_OPT - P=O(n**2/logn) with REPLICATE_OPT




########################################################################
############################### TESTS ##################################
########################################################################
if __name__ == '__main__':
	########################################################################
	## Testing REPLICATE
	########################################################################
	pram = MyPRAM({})
	d = 5
	cpy = [ None for i in range(2**5 +1) ]
	print ("\nTesting Replicate:")
	print ('Executing REPLICATE on datum %s, replicating %d times.' % (d, 2**5))
	pram.REPLICATE(cpy, d, 2**5)
	print (cpy)
	assert ([ d for i in range(2**5 +1) ][1:] == cpy[1:])

	########################################################################
	## Testing TOURNAMENT SORTING
	########################################################################
	vector_to_sort  = [ None ]
	n = 2**6	# <-- Must be a power of 2
	while len(vector_to_sort) < n+1:
		val = random.randint(0,10000)
		if val not in vector_to_sort:
			vector_to_sort.append(val)
	print ("\nTesting Tournament Sorting on vector:")
	print (vector_to_sort)

	# Create PRAM for tournement sorting CREW
	pram = MyPRAM({'a': vector_to_sort})
	print ('Executing TOURNAMENT_SORT_CREW on ' + str(n) + ' elements...')
	b = pram.TOURNAMENT_SORT_CREW(pram['a'], n)
	print (b)
	assert(b[1:] == sorted(vector_to_sort[1:]))

	# Create PRAM for tournement sorting EREW
	pram = MyPRAM({'a': vector_to_sort})
	print ('Executing TOURNAMENT_SORT_EREW on ' + str(n) + ' elements...')
	b = pram.TOURNAMENT_SORT_EREW(pram['a'], n)
	print (b)
	assert(b[1:] == sorted(vector_to_sort[1:]))

	########################################################################
	## Testing SUMMATIONS and PREFIX SUMS
	########################################################################
	n = 2**8	# <-- Number of elements to sum up
				#     It must be a power of 2, and for the OPTIMAL algorithms it
				#     must also be a power of a power of 2 (like 2, 2**2, 2**4, 2**8, 2**16, ..)!
	a = [ None for i in range(0, 2*n) ] # <-- Vector to sum up, it contains 1 extra element to allow indexing from 1
	for i in range(1, n):   a[i] = 0
	for i in range(n, 2*n): a[i] = random.randint(1,2)
	print ("\nTesting Summations on vector:")
	print (a)

	pram = MyPRAM({'a': a}) # We need 2n-1 nodes for the heap-structure PRAM
	print ('Executing SUM_PRAM...')
	s = pram.SUM_PRAM(pram['a'], n)
	print (s)
	assert s == sum(a[1:])

	pram = MyPRAM({'a': a}) # We need 2n-1 nodes for the heap-structure PRAM
	print ('Executing SUM_PRAM_OPT...')
	s = pram.SUM_PRAM_OPT(pram['a'], n)
	print (s)
	assert s == sum(a[1:])

	pram = MyPRAM({'a': a}) # We need 2n-1 nodes for the heap-structure PRAM
	print ('Executing ASSOCIATIVE_OP_PRAM(+)...')
	s = pram.ASSOCIATIVE_OP_PRAM(pram['a'], n, add)
	print (s)
	assert s == functools.reduce(add, a[1:])

	pram = MyPRAM({'a': a, 'b': [ None for i in range(0, 2*n) ]}) # We need 2n-1 nodes for the heap-structure PRAM
	print ('Executing PREFIX_SUM_PRAM...')
	pram.PREFIX_SUM_PRAM(pram['a'], pram['b'], n)
	print (pram['b'])
	assert pram['b'][n:] == [ sum(a[n:k]) for k in range(n+1, 2*n+1) ]

	print ("\nAll tests passed successfully!")
