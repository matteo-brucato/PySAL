#coding=utf-8
"""
PySAL - Python Synchronous Algorithms Library
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


class MyButterfly(Butterfly):
	
	########################################################################
	## SUMMATION ON BUTTERFLY
	########################################################################
	#;; SUM_BUTTERFLY
	def SUM_BUTTERFLY(self, propagate=False):
		k = self.k
		n = 2**k
		
		# Downwards sum, following the vertical links
		for i in range(1, k+1):
			forall (i,j) as P where j in range(0, n) do in parallel:
				P['b'] = P.getfrom('a', i-1, j)
				P['a'] = P['a'] + P['b']
		
		# Upwards sum, following the trees
		for i in reversed(range(k)):
			forall (i,j) as P where j in range(0, n) do in parallel using k:
				P['b'] = P.getfrom('a', i+1, j)
				P['c'] = P.getfrom('a', i+1, (j + 2**(k-1-i)) % 2**k)
				P['a'] = P['b'] + P['c']
		
		# Downwards propagation
		if not propagate: return
		for i in range(1, k+1):
			forall (i,j) as P where j in range(0, n) do in parallel:
				P['b'] = P.getfrom('a', i-1, j)
				P['a'] = P['b']
	#;;
	

########################################################################
############################### TESTS ##################################
########################################################################
if __name__ == '__main__':
	########################################################################
	## Testing SUMMATION ON BUTTERFLY
	########################################################################
	b = MyButterfly(3)
	b.randomfeed(-5,5)
	correctsum = sum([ P['a'] for P in b.iterprocs() ])
	print ("\nTesting Summation on", b)
	print ('Executing SUM_BUTTERFLY...')
	b.SUM_BUTTERFLY(True)
	print ('Resulting', b.str_variable('a'))
	assert(b.M[0][0]['a'] == correctsum)

	print ("\nAll tests passed successfully!")
