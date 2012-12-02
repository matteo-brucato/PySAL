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
import random

parallel = False

class Processor:
	"""
	A processor to be included in a SyncNet.
	"""
	
	def __init__(self, i, j=None):
		self.i = i
		self.j = j
		self.data  = {}
		self.tdata = {}
		self.nb = []
	
	def __str__(self):
		s = 'Processor(' + str(self.i) + ',' + str(self.j) + ')'
		return s
	
	def __deepcopy__(self, memo):
		x = Processor(self.i, self.j)
		memo[id(self)] = x
		for n, v in self.__dict__.items():
			setattr(x, n, copy.deepcopy(v, memo))
		return x
	
	def __setitem__(self, var, val):
		if parallel:
			self.tdata[var] = val
		else:
			self.data[var] = val
	
	def __getitem__(self, var, getnew=True):
		if parallel and getnew:
			if var in self.tdata:
				return self.tdata[var]
		else:
			if var in self.data:
				return self.data[var]

		raise Exception("Processor [" + str(self.i) + "," + str(self.j) + "] is asking for variable '"+str(var)+"' that has not been set yet")
	
	def getfrom(self, var, i, j=None, getnew=False):
		"""
		Read from a neighbor that has 'i' (and eventually 'j') as provided.
		If it exists, return the neighbor processor, otherwise raise an exception.
		If 'getnew' is True, it will read from 'tdata', otherwise from 'data'
		"""
		#~ print 'processor [%s:%s,%s] reads from processor [%s:%s,%s]' % \
			#~ (self.i, bin(self.i)[2:].zfill(6), self.j, i, bin(i)[2:].zfill(6), j)
		for P in self.nb:
			if P.i == i and P.j == j:
				return P.__getitem__(var, getnew)
		
		raise Exception('processor [' + str(self.i) + ',' + str(self.j) + ']' \
		  ' wants to read from processor [' + str(i)      + ',' + str(j)      + ']')
	
	def getindices(self):
		if self.j is None:
			return (self.i, )
		else:
			return (self.i, self.j)


class SyncNet(object):
	"""
	Every synchronous network must have the method forall_do_in_parallel().
	"""
	
	def forall_do_in_parallel(self, indices, func):
		global parallel
		#parallel = False		# Attualmente nested parallel loop non supportati
		
		# Create list of processors 'procs' out of the indices
		self.procs = [
			self.getproc(*ind) if isinstance(ind, (list, tuple)) else 
			self.getproc(ind)
				for ind in indices
		]
		
		# Copy data to temp
		#for P in self.iterprocs():
		for P in self.procs:
			for i in P.data:
				P.tdata[i] = P.data[i]
		
		# Execute 'func' over each processor in 'procs'
		parallel = True
		for P in self.procs:
			func(P, *P.getindices())
		parallel = False
		
		# Store back data
		for P in self.procs:
			for i in P.tdata:
				P.data[i] = P.tdata[i]
	
	def synchronize(self):
		"""
		End instruction synchronization, forced with ';'
		WARNING! THIS DOESN'T WORK, DON'T USE ';' IN PYSAL CODE
		"""
		# Store back data
		parallel = False
		for P in self.procs:
			for i in P.tdata:
				P.data[i] = P.tdata[i]
		
		# Copy data to temp
		#~ for P in self.iterprocs():
			#~ for i in P.data:
				#~ P.tdata[i] = P.data[i]
		parallel = True


class Mesh(SyncNet):
	
	def __init__(self, n, cyclic=False, toroidal=False):
		self.n = n
		# Create processors and store them in a private matrix
		self.M = [ Processor(i,j) for i in range(n) for j in range(n) ]
		# Link processors in Mesh
		for i in range(n-1):
			for j in range(n):
				# Horizontal
				self.M[i+n*j].nb     .append( self.M[i+n*j+1] )
				self.M[i+n*j+1].nb   .append( self.M[i+n*j]   )
				# Vertical
				self.M[n*i+j].nb     .append( self.M[n*(i+1)+j] )
				self.M[n*(i+1)+j].nb .append( self.M[n*i+j] )
		# Cyclic links
		if cyclic:
			for i in range(n):
				# Horizontal cycles
				self.M[n*i].nb       .append( self.M[n*(i+1)-1] )
				self.M[n*(i+1)-1].nb .append( self.M[n*i] )
				# Vertical cycles
				self.M[i].nb         .append( self.M[i+n*(n-1)] )
				self.M[i+n*(n-1)].nb .append( self.M[i] )
		# Toroidal links (TODO)
		if toroidal: pass
	
	def __str__(self):
		s = 'MESH:\n'
		for i,P in enumerate(self.M):
			for d in sorted(P.data):
				s += str(P[d]) + ','
			s += '\t'
			if i%self.n == self.n-1 and i < self.n*self.n -1: s += '\n\n'
		return s
	
	def iterprocs(self):
		for p in self.M:
			yield p
	
	def getproc(self, i, j):
		return self.M[self.n*i + j]
	
	def str_variable(self, d):
		s = 'MESH:\n'
		for i,P in enumerate(self.M):
			s += str(P[d]) + ','
			s += '\t'
		return s
	
	def variable(self, d):
		l = []
		for i,P in enumerate(self.M):
			l.append(P[d])
		return l
	
	def randomfeed(self, a, b, vars=['a']):
		for i,p in enumerate(self.M):
			for v in vars:
				self.M[i].data[v] = random.randint(a, b)


class Hypercube(SyncNet):
	
	def __init__(self, k):
		self.k = k
		# Create processors and store them in a private array
		self.M = [ Processor(i) for i in range(2**k) ]
		# Link processors in Hypercube
		for i in range(2**k):
			for h in range(k):
				try:
					self.M[i].nb        .append( self.M[i + 2**h] )
					self.M[i + 2**h].nb .append( self.M[i] )
				except: pass
	
	def __str__(self):
		s = 'HYPERCUBE:\n'
		for i,P in enumerate(self.M):
			s += str(P.i) + ':' + '('
			for d in sorted(P.data):
				s += str(P[d]) + ','
			s += ')\t'
		return s
	
	def iterprocs(self):
		for p in self.M:
			yield p
	
	def getproc(self, i):
		return self.M[i]
	
	def str_variable(self, d):
		s = 'HYPERCUBE:\n'
		for i,P in enumerate(self.M):
			s += str(P[d]) + ','
			s += '\t'
		return s
	
	def variable(self, d):
		l = []
		for i,P in enumerate(self.M):
			l.append(P[d])
		return l
	
	#~ def feed(self, d, vals):
		#~ raise Exception()
		#~ for i,p in enumerate(self.M):
			#~ self.M[i].data[d] = vals[i]
	
	def randomfeed(self, a, b, vars=['a']):
		for i,p in enumerate(self.M):
			for v in vars:
				self.M[i].data[v] = random.randint(a, b)


class Shuffle(SyncNet):
	
	def __init__(self, p):
		self.p = p
		self.n = 2**p
		# Create processors and store them in a private array
		self.M = [ Processor(i) for i in range(self.n) ]
		# Exchange links
		for i in range(self.n):
			if i%2==0 and (i+1)<self.n:	# For each 'i' even
				self.M[i]  .nb.append( self.M[i+1] )
				self.M[i+1].nb.append( self.M[i] )
		# Shuffle links
		for i in range(self.n -1):
			self.M[2*i % (self.n-1)].nb.append( self.M[i] )
		# Last shuffle link
		self.M[self.n-1].nb.append( self.M[self.n-1] )
	
	def __str__(self):
		s = 'SHUFFLE:\n'
		for i,P in enumerate(self.M):
			s += str(P.i) + ':' + '('
			for d in sorted(P.data):
				s += str(P[d]) + ','
			s += ')\t'
		return s
	
	def iterprocs(self):
		for p in self.M:
			yield p
	
	def getproc(self, i):
		return self.M[i]
	
	def str_variable(self, d):
		s = 'SHUFFLE:\n'
		for i,P in enumerate(self.M):
			s += str(P[d]) + ','
			s += '\t'
		return s
	
	def variable(self, d):
		l = []
		for i,P in enumerate(self.M):
			l.append(P[d])
		return l
	
	def randomfeed(self, a, b, vars=['a']):
		for i,p in enumerate(self.M):
			for v in vars:
				self.M[i].data[v] = random.randint(a, b)


class Butterfly(SyncNet):
	
	def __init__(self, k):
		self.k = k
		# Create processors and store them in a private matrix
		self.M = [ [ Processor(i,j) for j in range(2**k) ] for i in range(k+1) ]
		# Vertical links
		for i in range(k):
			for j in range(2**k):
				self.M[i]  [j].nb .append( self.M[i+1][j] )
				self.M[i+1][j].nb .append( self.M[i]  [j] )
		# Diagonal links
		for i in range(k):
			for j in range(2**k):
				self.M[i]  [j].nb                       .append( self.M[i+1][(j + 2**(k-1-i)) % 2**k] )
				self.M[i+1][(j + 2**(k-1-i)) % 2**k].nb .append( self.M[i]  [j] )
	
	def __str__(self):
		s = 'BUTTERFLY:\n'
		for row in self.M:
			for P in row:
				# Print all set variables of processor P
				for d in sorted(P.data):
					s += str(P[d]) + ','
				s += '\t'
			if self.M.index(row) < len(self.M)-1: s += '\n'
		return s
	
	def str_variable(self, d):
		s = 'BUTTERFLY:\n'
		for row in self.M:
			for P in row:
				s += str(P[d]) + '\t'
			if self.M.index(row) < len(self.M)-1: s += '\n'
		return s
	
	def variable(self, d):
		v = []
		for row in self.M:
			for P in row:
				v.append(P[d])
		return v
		
	def iterprocs(self):
		for prow in self.M:
			for p in prow:
				yield p
	
	def getproc(self, i, j):
		return self.M[i][j]
	
	def randomfeed(self, a, b, vars=['a']):
		for i,row in enumerate(self.M):
			for j,el in enumerate(row):
				for v in vars:
					self.M[i][j].data[v] = random.randint(a, b)
