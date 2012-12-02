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

class MyShuffle(Shuffle):
	
	########################################################################
	## SUMMATION ON SHUFFLE
	########################################################################
	#;; SUM_SHUFFLE
	def SUM_SHUFFLE(self):
		logn = self.p
		n = self.n
		
		for i in range(1, logn+1):
			forall j as P where j in range(0, n) do in parallel using i,n:
				# MESCOLA
				if j%2==0:
					P['a'] = P.getfrom('a', j//2)
				else:
					P['a'] = P.getfrom('a', (n+j-1)//2)
				
				P['b'] = P['a']
			
			forall j as P where j in range(0, n) do in parallel using i,n:
				# SCAMBIA
				if j%2==0:
					P['b'] = P.getfrom('b', j+1)
				else:
					P['b'] = P.getfrom('b', j-1)
				
				# SOMMA
				P['a'] = P['a'] + P['b']
	#;;
	


########################################################################
############################### TESTS ##################################
########################################################################
if __name__ == '__main__':
	########################################################################
	## Testing SUMMATION ON BUTTERFLY
	########################################################################
	b = MyShuffle(7)
	b.randomfeed(-5,5, vars=['a','b'])
	correctsum = sum([ P['a'] for P in b.iterprocs() ])
	print ("\nTesting Summation on", b)
	print ('Executing SUM_SHUFFLE...')
	b.SUM_SHUFFLE()
	print ('Resulting', b)
	assert(b.M[0]['a'] == correctsum)

	print ("\nAll tests passed successfully!")
