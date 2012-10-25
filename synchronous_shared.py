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
from copy import *

parallel = False
process  = None

class PRAMSyncVect(list):
	"""
	A vector to be used in synchronous parallelism, in PRAMs.
	"""
	
	def __init__(self, l):
		self.tempvector = copy(l)
		super(PRAMSyncVect, self).__init__(l)
		self.writtenby = None
	
	def __setitem__(self, i, val):
		if parallel:
			self.tempvector[i] = val
		else:
			super(PRAMSyncVect, self).__setitem__(i, val)
		
		self.writtenby = process
	
	def __getitem__(self, i):
		if parallel and self.writtenby == process:
			return self.tempvector[i]
		else:
			# If self.writtenby != process means that this sync vector
			# has been lastly overwritten by another parallel process.
			# Since we are simulating sync parallelism, the current process
			# should read old values from this vector, hence not read
			# from tempvector (which holds new values).
			return super(PRAMSyncVect, self).__getitem__(i)


class PRAM:
	
	def __init__(self, vectors):
		self.vectors = {}
		for v in vectors:
			self.vectors[v] = PRAMSyncVect(vectors[v])
	
	def __setitem__(self, name, vector):
		self.vectors[name] = PRAMSyncVect(vector)
	
	def __getitem__(self, name):
		return self.vectors[name]
	
	def __str__(self):
		s = 'PRAM:\n'
		for i,P in enumerate(self.M):
			for d in sorted(P.data):
				s += str(P.get(d)) + ','
			s += '  '
		return s
	
	def forall_do_in_parallel(self, indices, func):
		global parallel, process
		was_already_parallel = parallel      # for nested parallel loops
		
		#parallel = False
		
		# Copy data to temporal vectors
		if not was_already_parallel:	# If nested parallel loop (esample when calling SUM inside loops), skip this
			for name,vec in self.vectors.items():
				for i in range(len(vec)):
					vec.tempvector[i] = vec[i]
		
		# Execute 'func' over each processor 'i' in 'indices'
		parallel = True
		for i in indices:
			process = i
			if isinstance(i, (tuple, list)):
				func(*i)
			else:
				func(i)
		parallel = False
		
		# Store back data, after "parallel" execution
		for name,vec in self.vectors.items():
			for i in range(len(vec)):
				vec[i] = vec.tempvector[i]
		
		parallel = was_already_parallel
		process  = None
	
