#!/usr/bin/python
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
from __future__ import print_function
import sys, os

class CommentExc(Exception): pass
class SintaxError(Exception): pass
class IndentError(Exception): pass

def add_line_sync(line, indents):
	"""
	This function replaces ";" with synchronization calls.
	"""
	return line.replace(';', '\n%sself.synchronize()' % (indents,))

if len(sys.argv) < 2:
	print('Usage...', file=sys.stderr)
	sys.exit(1)

filename = sys.argv[1]
filein  = open(filename, 'r')
#fileout = open('out_algorithms'+ os.sep + os.path.basename(filename).replace('.pysal', ''), 'w')
fileout = open('out_' + os.path.basename(filename).replace('.pysal', ''), 'w')

parallel_funcs = []
foralllines = []
lines = []

# STATES
FORALL = 0
BODYFUNC = 1

procnum = 0
l = -1
state = FORALL
for line in filein:
	
	lines.append(line)
	l += 1
	
	if state == BODYFUNC:
		indents2 = 0
		try:
			# Conta indentazioni del corpo funzione
			for c in line:
				if c == '#':
					raise CommentExc
				if c == ' ' or c == '\t':
					indents2 += 1
					intentype = c
				else:
					break
			
			if diffindents is None:
				diffindents = indents2 - indents
				if diffindents <= 0:
					raise IndentError
				body.append(add_line_sync(line, intentype*indents2))
				foralllines.append(l)
			else:
				if indents2 - indents < diffindents:
					
					# Fine definizione funzione
			
					parallel_funcs.append({
						'l': funcline,
						'elem': elem,
						'elemname': elemname,
						'forloop': forloop,
						'funcname': 'par_proc_' + str(procnum),
						'usings': usings,
						'indents': funcindents,
						'body': body,
					})
					procnum += 1
					
					state = FORALL
				else:
					body.append(add_line_sync(line, intentype*indents2))
					foralllines.append(l)
			
		except CommentExc:
			continue
		
		except IndentError:
			print ('Indentation Error', file=sys.stderr)
			sys.exit(3)
	
	if state == FORALL:
		if line.find('forall') != -1 and line.find('where') != -1 and line.find('do in parallel') != -1:
			indents = 0
			try:
				for c in line:
					if c == '#':
						raise CommentExc
					if c == ' ' or c == '\t':
						indents += 1
					else:
						break
					
				if not line[indents: indents+6] == 'forall':
					raise SintaxError
				
				aspos = line.find('as ')
				if aspos != -1:
					wherepos = line[aspos:].find('where ') + aspos
					elem = line[indents+len('forall'): aspos]
					elemname = line[aspos+len('as'): wherepos]
				else:
					wherepos = line.find('where ')
					elem = line[indents+len('forall'): wherepos]
					elemname = elem
				
				# Pick variable names in all "where" statements
				#lastwherepos = wherepos
				#while True:
				#	lastwherepos = line[lastwherepos:].find('where ') + lastwherepos
				#	if lastwherepos == -1: break
						
				
				doparpos = line[wherepos:].find('do in parallel') + wherepos
				usingpos = line[doparpos:].find('using') + doparpos
				forloop = line[wherepos+len('where'): doparpos]
				if usingpos > doparpos: usings = line[usingpos+len('using'): line.find(':')]
				else:                   usings = ''
				
				funcline = l
				funcindents = line[:indents]
				foralllines.append(l)
				diffindents = None
				body = []
				state = BODYFUNC
				
			except CommentExc:
				continue
			
			except SintaxError:
				print('Sintax Error on line %d:\n%s' % (l+1, line), file=sys.stderr)
				sys.exit(2)


print ('from __future__ import print_function', file=fileout)
print ('#coding=utf-8', file=fileout)

for f in parallel_funcs:
	funcname = f['funcname']
	elem = f['elem']
	elemname = f['elemname']
	usings = 'self,' + f['usings']
	body = f['body']
	print ('def %s(%s%s%s):' % (funcname, elemname.replace('(','').replace(')',''), '' if elem==elemname else ','+elem.replace('(','').replace(')',''), '' if usings=='' else ','+usings), file=fileout)
	for l in body:
		print ('%s' % (l), file=fileout, end='')

print ('\n\n', file=fileout)

for i in range(len(lines)):
	if i not in foralllines:
		print (lines[i], file=fileout, end='')
	else:
		for f in parallel_funcs:
			if f['l'] == i:
				funcname = f['funcname']
				elem = f['elem']
				elemname = f['elemname']
				forloop = f['forloop'].replace('where','for')
				funcindents = f['indents']
				usings = 'self,' + f['usings']
				print ("%sself.forall_do_in_parallel([%s for %s], lambda %s%s:" % (funcindents, elem, forloop, elemname.replace('(','').replace(')',''), '' if elem==elemname else ','+elem.replace('(','').replace(')','')), file=fileout)
				print ("%s\t%s(%s%s%s)" % (funcindents, funcname, elemname.replace('(','').replace(')',''), '' if elem==elemname else ','+elem.replace('(','').replace(')',''), '' if usings=='' else ','+usings), file=fileout)
				print ("%s)" % funcindents, file=fileout)
				break
		else:
			#print (output[i], end='')
			pass
