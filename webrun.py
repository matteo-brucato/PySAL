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
import sys, time, string, cgi, time, json, math, random
from math import log
from numpy import matrix
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.runtime import Context
from StringIO import StringIO

from out_PRAM import *
from out_HYPERCUBE import *
from out_BUTTERFLY import *
from out_MESH import *
from out_SHUFFLE import *


HOST_NAME = 'localhost'
PORT_NUMBER = 8001


def get_algorithm(filename, func_name):
	state = None
	s = ''
	f = open(filename)
	
	for line in f:	
		if line.strip().startswith('#;;'):
			if state == 1:
				break
			if line.strip()[3:].strip() == func_name:
				state = 1
		
		elif state == 1:
			s += line
	
	return s

def is_power2(num):
	if type(num) is float: num = int(num)
	return num != 0 and ((num & (num - 1)) == 0)


# POST FUNCTIONS
def pram_replicate(query):
	pram = MyPRAM({})
	datum = eval(query.get('datum')[0])
	ncopies = eval(query.get('ncopies')[0])
	if not is_power2(ncopies):
		raise Exception('"n" must be power of 2')
	cpy = [ None for i in range(ncopies +1) ]
	print ("\nTesting Replicate:")
	print ('Executing REPLICATE on datum %s, replicating %d times.' % (datum, ncopies))
	pram.REPLICATE(cpy, datum, ncopies)
	print (cpy)
	#assert ([ datum for i in range(ncopies +1) ][1:] == cpy[1:])
	return json.dumps({'result': str(cpy[1:])})

def pram_sum(query):
	ainput = eval(query.get('a')[0])
	n = len(ainput)
	if not is_power2(n):
		raise Exception('"n" must be power of 2')
	a = [ None for i in range(0, 2*n) ] # <-- Vector to sum up, it contains 1 extra element to allow indexing from 1
	for i in range(1, n):   a[i] = 0
	for i in range(n, 2*n): a[i] = ainput[i-n]
	pram = MyPRAM({'a': a})
	print ('Executing SUM_PRAM...')
	s = pram.SUM_PRAM(pram['a'], n)
	print (s)
	#assert s == sum(ainput)
	return json.dumps({'input': str(ainput), 'result': str(s)})

def pram_sum_opt(query):
	ainput = eval(query.get('a')[0])
	n = len(ainput)
	if not is_power2(n) or not is_power2(log(n,2)):
		raise Exception('"n" and log("n") must be both power of 2')
	a = [ None for i in range(0, 2*n) ] # <-- Vector to sum up, it contains 1 extra element to allow indexing from 1
	for i in range(1, n):   a[i] = 0
	for i in range(n, 2*n): a[i] = ainput[i-n]
	pram = MyPRAM({'a': a})
	print ('Executing SUM_PRAM_OPT...')
	s = pram.SUM_PRAM_OPT(pram['a'], n)
	print (s)
	#assert s == sum(ainput)
	return json.dumps({'input': str(ainput), 'result': str(s)})

def pram_prefix_sum(query):
	ainput = eval(query.get('a')[0])
	n = len(ainput)
	if not is_power2(n):
		raise Exception('"n" must be power of 2')
	a = [ None for i in range(0, 2*n) ] # <-- Vector to sum up, it contains 1 extra element to allow indexing from 1
	for i in range(1, n):   a[i] = 0
	for i in range(n, 2*n): a[i] = ainput[i-n]
	pram = MyPRAM({'a': a, 'b': [ None for i in range(0, 2*n) ]})
	print ('Executing SUM_PRAM...')
	pram.PREFIX_SUM_PRAM(pram['a'], pram['b'], n)
	print (pram['b'])
	#assert s == sum(ainput)
	return json.dumps({'input': str(ainput), 'result': str(pram['b'][n:])})

def pram_tournament_crew(query):
	try:
		vector_to_sort = [None] + eval(query.get('a')[0])
	except:
		try:
			nn = int(eval(query.get('a')[0][7: query.get('a')[0].find(')')]))
			vector_to_sort = [None]
			while len(vector_to_sort) < nn+1:
				val = random.randint(-10000,10000)
				if val not in vector_to_sort:
					vector_to_sort.append(val)
		except:
			raise Exception('"a" must be a vector of distinct integers, or the string "random(n)" with "n" positive integer')
	n = len(vector_to_sort) - 1
	if not is_power2(n):
		raise Exception('"n" must be power of 2')
	if len(vector_to_sort) != len(set(vector_to_sort)):
		raise Exception('input vector must contain distinct elements')
	pram = MyPRAM({'a': vector_to_sort})
	print ('Executing TOURNAMENT_SORT_CREW on ' + str(n) + ' elements...')
	b = pram.TOURNAMENT_SORT_CREW(pram['a'], n)
	print (b)
	return json.dumps({'input': str(vector_to_sort[1:]), 'result': str(b[1:])})

def pram_tournament_erew(query):
	try:
		vector_to_sort = [None] + eval(query.get('a')[0])
	except:
		try:
			nn = int(eval(query.get('a')[0][7: query.get('a')[0].find(')')]))
			vector_to_sort = [None]
			while len(vector_to_sort) < nn+1:
				val = random.randint(-10000,10000)
				if val not in vector_to_sort:
					vector_to_sort.append(val)
		except:
			raise Exception('"a" must be a vector of distinct integers, or the string "random(n)" with "n" positive integer')
	n = len(vector_to_sort) - 1
	if not is_power2(n):
		raise Exception('"n" must be power of 2')
	if len(vector_to_sort) != len(set(vector_to_sort)):
		raise Exception('input vector must contain distinct elements')
	pram = MyPRAM({'a': vector_to_sort})
	print ('Executing TOURNAMENT_SORT_EREW on ' + str(n) + ' elements...')
	b = pram.TOURNAMENT_SORT_EREW(pram['a'], n)
	print (b)
	return json.dumps({'input': str(vector_to_sort[1:]), 'result': str(b[1:])})

def hyper_sum(query):
	propagate = eval(query.get('propagate')[0])
	a = eval(query.get('a')[0])
	n = len(a)
	if not is_power2(n):
		raise Exception('the lenght of the vector "a" must be a power of 2')
	h = MyHypercube(int(log(n,2)))
	#h.randomfeed(0,3)
	for i in range(n):
		h.M[i]['a'] = a[i]
	#correctsum = sum([ h.M[i]['a'] for i in range(len(h.M)) ])
	#h.feed('a', [5,6,3,13,7,10,9,2])
	print ("\nTesting Summation on", h.str_variable('a'))
	print ('Executing SUM_HYPERCUBE...')
	h.SUM_HYPERCUBE(propagate)
	print ('Resulting', h.str_variable('a'))
	#assert(h.M[0]['a'] == correctsum)
	return json.dumps({'input': str(a), 'result': str(h.variable('a'))})

def hyper_bitonic(query):
	a = eval(query.get('a')[0])
	n = len(a)
	if not is_power2(n):
		raise Exception('the lenght of the vector "a" must be a power of 2')
	h = MyHypercube(int(log(n,2)))
	#h.randomfeed(0,3)
	for i in range(n):
		h.M[i]['a'] = a[i]
	#correctsum = sum([ h.M[i]['a'] for i in range(len(h.M)) ])
	#h.feed('a', [5,6,3,13,7,10,9,2])
	print ("\nTesting Summation on", h.str_variable('a'))
	print ('Executing BITONIC_MERGESORT_HYPERCUBE...')
	h.BITONIC_MERGESORT_HYPERCUBE()
	print ('Resulting', h.str_variable('a'))
	#assert(h.M[0]['a'] == correctsum)
	return json.dumps({'input': str(a), 'result': str(h.variable('a'))})

def hyper_multmatrix(query):
	A = matrix(query.get('A')[0]).tolist()
	B = matrix(query.get('B')[0]).tolist()
	if not len(A) == len(B):
		raise Exception('the size of the matrices must be equal')
	n = len(A)
	if not is_power2(n):
		raise Exception('the size of the matrices must be a power of 2')
	h = MyHypercube(3*int(log(n,2)))
	#h.randomfeed(0,3)
	for i in range(n):
		for j in range(n):
			h.M[n*i+j]['A'] = A[i][j]
			h.M[n*i+j]['B'] = B[i][j]
	#correctsum = sum([ h.M[i]['a'] for i in range(len(h.M)) ])
	#h.feed('a', [5,6,3,13,7,10,9,2])
	print ("\nTesting Matrix Multiplication on", h)
	print ('Executing MATRIX_MULTIPLICATION_HYPERCUBE...')
	h.MATRIX_MULTIPLICATION_HYPERCUBE()
	print ('Resulting', h.str_variable('C'))
	#assert(h.M[0]['a'] == correctsum)
	resultmatrix_ = h.variable('C')[:n*n]
	print resultmatrix_
	resultmatrix = []
	i = 0
	while i < len(resultmatrix_):
		row = []
		while len(row) < n:
			row.append(resultmatrix_[i])
			i += 1
		resultmatrix.append(row)
	print resultmatrix
	return json.dumps({
		'input': 'A: <pre>' + str(matrix(A)) + '</pre>B: <pre>' + str(matrix(B)) +'</pre>',
		'result': '<pre>' + str(matrix(resultmatrix)) + '</pre>'
	})

def butterfly_sum(query):
	propagate = eval(query.get('propagate')[0])
	k = eval(query.get('k')[0])
	a = eval(query.get('a')[0])
	n = len(a)
	if n != (k+1)*(2**k):
		raise Exception('the lenght of the vector "a" must be equal to n=(k+1)*(2**k)')
	b = MyButterfly(k)
	#h.randomfeed(0,3)
	for i in range(k+1):
		for j in range(2**k):
			b.M[i][j]['a'] = a[i*(2**k)+j]
	#correctsum = sum([ h.M[i]['a'] for i in range(len(h.M)) ])
	#h.feed('a', [5,6,3,13,7,10,9,2])
	print ("\nTesting Summation on", b.str_variable('a'))
	print ('Executing SUM on butterfly...')
	b.SUM_BUTTERFLY(propagate)
	print ('Resulting', b.str_variable('a'))
	#assert(h.M[0]['a'] == correctsum)
	input_butterfly_ = a
	input_butterfly = []
	i = 0
	while i < len(input_butterfly_):
		row = []
		while len(row) < 2**k:
			row.append(input_butterfly_[i])
			i += 1
		input_butterfly.append(row)
	output_butterfly_ = b.variable('a')
	output_butterfly = []
	i = 0
	while i < len(input_butterfly_):
		row = []
		while len(row) < 2**k:
			row.append(output_butterfly_[i])
			i += 1
		output_butterfly.append(row)
	return json.dumps({
		'input':  '<pre>' + str(matrix(input_butterfly)) + '</pre>',
		'result': '<pre>' + str(matrix(output_butterfly)) + '</pre>'
	})

def mesh_sum(query):
	propagate = eval(query.get('propagate')[0])
	a = eval(query.get('a')[0])
	n = len(a)
	p = math.sqrt(n)
	if not p.is_integer():
		raise Exception('the lenght of the vector "a" must be equal to n=p**2 for a positive integer p')
	else:
		p = int(p)
	b = MyMesh(p)
	#h.randomfeed(0,3)
	for i in range(p*p):
		b.M[i]['a'] = a[i]
	#correctsum = sum([ h.M[i]['a'] for i in range(len(h.M)) ])
	#h.feed('a', [5,6,3,13,7,10,9,2])
	print ("\nTesting Summation on", b.str_variable('a'))
	print ('Executing SUM_MESH...')
	b.SUM_MESH(propagate)
	print ('Resulting', b.str_variable('a'))
	#assert(h.M[0]['a'] == correctsum)
	input_mesh_ = a
	input_mesh = []
	i = 0
	while i < len(input_mesh_):
		row = []
		while len(row) < p:
			row.append(input_mesh_[i])
			i += 1
		input_mesh.append(row)
	output_mesh_ = b.variable('a')
	output_mesh = []
	i = 0
	while i < len(output_mesh_):
		row = []
		while len(row) < p:
			row.append(output_mesh_[i])
			i += 1
		output_mesh.append(row)
	return json.dumps({
		'input':  '<pre>' + str(matrix(input_mesh)) + '</pre>',
		'result': '<pre>' + str(matrix(output_mesh)) + '</pre>'
	})

def mesh_multmatrix(query):
	a = matrix(query.get('a')[0]).tolist()
	b = matrix(query.get('b')[0]).tolist()
	if not len(a) == len(b):
		raise Exception('the size of the matrices must be equal')
	n = len(a)*len(a)
	p = math.sqrt(n)
	if not p.is_integer():
		raise Exception('the size of the matrices "a" and "b" must be equal to nxn where n=p**2 for a positive integer p')
	else:
		p = int(p)
	h = MyMesh(p, cyclic=True)
	for i in range(p):
		for j in range(p):
			h.M[p*i+j]['a'] = a[i][j]
			h.M[p*i+j]['b'] = b[i][j]
	print ("\nTesting Summation on", h.str_variable('a'))
	print ('Executing MATRIX_MULTIPLICATION_CYCLIC_MESH...')
	h.MATRIX_MULTIPLICATION_CYCLIC_MESH()
	print ('Resulting', h.str_variable('c'))
	#assert(h.M[0]['a'] == correctsum)
	output_mesh_ = h.variable('c')
	print output_mesh_
	output_mesh = []
	i = 0
	while i < n:
		row = []
		while len(row) < p:
			row.append(output_mesh_[i])
			i += 1
		output_mesh.append(row)
	print output_mesh
	return json.dumps({
		'input':  '<pre>a:<br />' + str(matrix(a)) + '</pre><pre>b:<br />' + str(matrix(b)) + '</pre>',
		'result': '<pre>' + str(matrix(output_mesh)) + '</pre>'
	})

def shuffle_sum(query):
	a = eval(query.get('a')[0])
	n = len(a)
	if not is_power2(n):
		raise Exception('the lenght of the vector "a" must be a power of 2')
	#~ if n < 1:
		#~ raise Exception('the lenght of the vector "a" must be at least 1')
	print n
	print log(n,2)
	b = MyShuffle(int(log(n,2)))
	for i in range(n):
		b.M[i]['a'] = a[i]
	#b.randomfeed(-5,5, vars=['a','b'])
	#correctsum = sum([ P['a'] for P in b.iterprocs() ])
	print ("\nTesting Summation on", b)
	print ('Executing SUM_SHUFFLE...')
	b.SUM_SHUFFLE()
	print ('Resulting', b)
	#assert(b.M[0]['a'] == correctsum)
	return json.dumps({'input': str(a), 'result': str(b.variable('a'))})




# Where to look for inherited and included templates
lookup = TemplateLookup(
	directories=['.'],
	input_encoding='utf-8',
	output_encoding='utf-8',
	encoding_errors='replace')

def view_template(templatefile, code=None):
	template = Template(filename=templatefile, lookup=lookup)
	return template.render_unicode(code=code).encode('utf-8', 'replace')

def execute_query(func, query):
	try:
		return func(query)
	except Exception as e:
		return json.dumps({'error': str(e)})

class Router:
	def __init__(self):
		pass
	
	def route(self, path, query=None):
		print path
		
		if path == '/':
			return view_template('templates/index.html')
		if path == '/credits':
			return view_template('templates/credits.html')
		
		if path == '/pram':
			return view_template('templates/pram/pram.html')
		if path == '/pram/replicate':
			return view_template('templates/pram/replicate.html',
				get_algorithm('algorithms/PRAM.pysal.py', 'REPLICATE'))
		if path == '/pram/sum':
			return view_template('templates/pram/sum.html',
				get_algorithm('algorithms/PRAM.pysal.py', 'SUM_PRAM'))
		if path == '/pram/sum_opt':
			return view_template('templates/pram/sum_opt.html',
				get_algorithm('algorithms/PRAM.pysal.py', 'SUM_PRAM_OPT'))
		if path == '/pram/prefix_sum':
			return view_template('templates/pram/prefix_sum.html',
				get_algorithm('algorithms/PRAM.pysal.py', 'PREFIX_SUM_PRAM'))
		if path == '/pram/tournament_crew':
			return view_template('templates/pram/tournament_crew.html',
				get_algorithm('algorithms/PRAM.pysal.py', 'TOURNAMENT_SORT_CREW'))
		if path == '/pram/tournament_erew':
			return view_template('templates/pram/tournament_erew.html',
				get_algorithm('algorithms/PRAM.pysal.py', 'TOURNAMENT_SORT_EREW'))
		
		if path == '/hyper':
			return view_template('templates/hyper/hyper.html')
		if path == '/hyper/sum':
			return view_template('templates/hyper/sum.html',
				get_algorithm('algorithms/HYPERCUBE.pysal.py', 'SUM_HYPERCUBE'))
		if path == '/hyper/bitonic':
			return view_template('templates/hyper/bitonic.html',
				get_algorithm('algorithms/HYPERCUBE.pysal.py', 'BITONIC_MERGESORT_HYPERCUBE'))
		if path == '/hyper/multmatrix':
			return view_template('templates/hyper/multmatrix.html',
				get_algorithm('algorithms/HYPERCUBE.pysal.py', 'MATRIX_MULTIPLICATION_HYPERCUBE'))
		
		if path == '/butterfly':
			return view_template('templates/butterfly/butterfly.html')
		if path == '/butterfly/sum':
			return view_template('templates/butterfly/sum.html',
				get_algorithm('algorithms/BUTTERFLY.pysal.py', 'SUM_BUTTERFLY'))
		
		if path == '/mesh':
			return view_template('templates/mesh/mesh.html')
		if path == '/mesh/sum':
			return view_template('templates/mesh/sum.html',
				get_algorithm('algorithms/MESH.pysal.py', 'SUM_MESH'))
		if path == '/mesh/multmatrix':
			return view_template('templates/mesh/multmatrix.html',
				get_algorithm('algorithms/MESH.pysal.py', 'MATRIX_MULTIPLICATION_CYCLIC_MESH'))
		
		if path == '/shuffle':
			return view_template('templates/shuffle/shuffle.html')
		if path == '/shuffle/sum':
			return view_template('templates/shuffle/sum.html',
				get_algorithm('algorithms/SHUFFLE.pysal.py', 'SUM_SHUFFLE'))
		
		if path == '/pram/replicate/exec':
			return execute_query(pram_replicate, query)
		if path == '/pram/sum/exec':
			return execute_query(pram_sum, query)
		if path == '/pram/sum_opt/exec':
			return execute_query(pram_sum_opt, query)
		if path == '/pram/prefix_sum/exec':
			return execute_query(pram_prefix_sum, query)
		if path == '/pram/tournament_crew/exec':
			return execute_query(pram_tournament_crew, query)
		if path == '/pram/tournament_erew/exec':
			return execute_query(pram_tournament_erew, query)
		if path == '/hyper/sum/exec':
			return execute_query(hyper_sum, query)
		if path == '/hyper/bitonic/exec':
			return execute_query(hyper_bitonic, query)
		if path == '/hyper/multmatrix/exec':
			return execute_query(hyper_multmatrix, query)
		if path == '/butterfly/sum/exec':
			return execute_query(butterfly_sum, query)
		if path == '/mesh/sum/exec':
			return execute_query(mesh_sum, query)
		if path == '/mesh/multmatrix/exec':
			return execute_query(mesh_multmatrix, query)
		if path == '/shuffle/sum/exec':
			return execute_query(shuffle_sum, query)
		
		raise Exception('No routing rule for %s' % path)
	
	



class MyHandler(BaseHTTPRequestHandler):
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
	
	def do_GET(self):
		try:
			if self.path.endswith(".html"):
				f = open(curdir + sep + self.path)
				self.send_response(200)
				self.send_header('Content-type',	'text/html')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			elif self.path.endswith(".js") or self.path.endswith(".css"):
				f = open(self.path[1:])
				self.send_response(200)
				if self.path.endswith(".css"):
					self.send_header('Content-type',	'text/css')
				if self.path.endswith(".js"):
					self.send_header('Content-type',	'application/javascript')
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			else:   #our dynamic content
				while self.path[-1] == '/' and self.path != '/':
					self.path = self.path[:len(self.path)-1]
				
				self.send_response(200)
				self.send_header('Content-type',	'text/html')
				self.end_headers()
				
				self.wfile.write(router.route(self.path))
				#self.wfile.write("hey, today is the" + str(time.localtime()[7]))
				#self.wfile.write(" day in the year " + str(time.localtime()[0]))
				
			return
				
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	def do_POST(self):
		global rootnode
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'multipart/form-data':
				query = cgi.parse_multipart(self.rfile, pdict)
			elif ctype == 'application/x-www-form-urlencoded':
				length = int(self.headers.getheader('content-length'))
				query = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
			else:
				query=None
			#self.send_response(301)
			#self.end_headers()
			self.send_response(200)
			self.send_header('Content-type',	'text/html')
			self.end_headers()
			self.wfile.write(router.route(self.path, query))
			
			#upfilecontent = query.get('upfile')
			#print "filecontent", upfilecontent[0]
			#self.wfile.write("<HTML>POST OK.<BR><BR>");
			#self.wfile.write(upfilecontent[0]);
			
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)




def main():
	global router
	router = Router()
	try:
		server = HTTPServer((HOST_NAME, PORT_NUMBER), MyHandler)
		print 'Started http server on %s:%d...' % (HOST_NAME, PORT_NUMBER)
		server.serve_forever()
	except KeyboardInterrupt:
		print ' Manual interrupt received. Server shut down.'
		server.socket.close()

if __name__ == '__main__':
	main()
