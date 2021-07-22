import matplotlib.pyplot as plt

import matplotlib
from math import sqrt, log
SPINE_COLOR = 'gray'
import subprocess
# print(plt.style.available)
plt.style.use('seaborn-colorblind')
import re
import json
import itertools
import functools

def parse_map(mapfile):
	print(mapfile)
	content = open(mapfile, 'r')
	result = {}
	reversed = {}

	originals = set()
	meta_names = {

	}

	# preprocess to idenify dispatchers
	lines = content.read().split("\n")
	for line in lines:
		fname, id = line.split(",")
		# demangle fname?
		
		meta = {}

		if fname.endswith("_original"):
			meta['isOriginal'] = True
			originals.add(fname.replace("_original", ""))

	for line in lines:
		fname, id = line.split(",")
		meta = {}


		meta['parent'] = re.sub(r"\.\d+$", "", fname)
		meta['parent'] = re.sub(r"_\d+_$", "", meta['parent'])
		meta['parent'] = meta['parent'].replace("_original", "")
		
		if fname.endswith("_original"):
			meta['isOriginal'] = True
			originals.add(fname.replace("_original", ""))
		else:
			meta['isOriginal'] = False

		if re.sub(r"\.\d+$", "", fname) in originals: # may be a dispatcher
			meta['isDispatcher'] = True
		else:
			meta['isDispatcher'] = False

		if re.compile(r"(.*)_\d+_$").match(fname): # is a variant
			# print("Variant", fname)
			meta['isVariant'] = True
		else:
			meta['isVariant'] = False

		meta['name'] = fname
		result[int(id)] = meta
		reversed[fname] = {
			'group': int(id)
		}


	#print(result)
	return result, reversed

def get_zero_degree_functions(file):
	content = open(file, 'r')
	lines = content.read().split("\n")
	result = []

	for line in lines:
		fname = line
		fname = fname.strip()
		if fname:
			result.append(fname)

	return result


def parsecfg(file):
	content = open(file, 'r')
	paths = content.read().split("\n")

	result = []
	for p in paths:
		functions = p.split(",")

		for i,f in enumerate(functions[1:]):
			fname = f.strip()
			previous = functions[i -1].strip()
			
			if fname and previous:
				t = (previous, fname)
				if t not in result:
					result.append(t)

	return result

def parseedges(file):
	content = open(file, 'r')
	edges = content.read().split("\n")

	result = []
	for p in edges:
		edge = p.split(",")

		if len(edge) != 2:
			continue
		e1, e2 = edge
		
		result.append((e1, e2))

	return result

def parse_functions(mapfile):
	print(mapfile)
	content = open(mapfile, 'r')
	result = {}
	reversed = {}
	originals = set()

	# preprocess to idenify dispatchers
	lines = content.read().split("\n")
	for line in lines:
		fname = line
		fname = fname.strip()
		meta = {}

		if fname.endswith("_original"):
			meta['isOriginal'] = True
			originals.add(fname.replace("_original", ""))
	count = 1
	print(originals)
	for line in lines:
		fname = line
		fname = fname.strip()
		id = count
		meta = {}

		if fname.endswith("_original"):
			meta['isOriginal'] = True
			originals.add(fname.replace("_original", ""))
		else:
			meta['isOriginal'] = False

		if re.sub(r"\.\d+", "", fname) in originals:
			meta['isDispatcher'] = True
		else:
			meta['isDispatcher'] = False

		if re.compile(r"(.*)_\d+_").match(fname): # is a variant
			print("Variant", fname)
			meta['isVariant'] = True
		else:
			meta['isVariant'] = False

		meta['name'] = fname
		result[id] = meta
		reversed[fname] = id
		count +=1 
	return result, reversed

def parse_static(mapfile):
	content = open(mapfile, 'r').read()

	lines = content.split("\n")
	edges_set = set()
	for line in lines:
		caller, called = line.split(",")
		caller = caller.strip()
		called = called.strip()

		edges_set.add((caller, called))


	return list(edges_set)

def calculate_preserved_cache(resultjson):
	CACHE = {}

	for k, v in resultjson.items():
		if 'functions' in v and 'pairs' in v:
			if type(v['functions']) is list:
				fs = v['functions']
			else:
				fs = [v['functions']]

			#print(fs)
			c = sum([1 if p[0]['isPreserved'] else 0 for p in v['pairs']])
			t = len(v['pairs'])
		

			for f in fs:
				CACHE[f] = [t, c]

	return CACHE


FAIL_IN_UNCONSISTENCY=True
def get_preservation_for_function(resultjson, fname):

	for k, v in resultjson.items():
		if 'functions' in v and fname in v['functions']:
			try:
				c = sum([1 if p[0]['isPreserved'] else 0 for p in v['pairs']])
				t = len(v['pairs'])
			
				#print(fname, t, c)
				return [t, c]
			except Exception as e:
				print("Error in", k, e, fname)

				if FAIL_IN_UNCONSISTENCY:
					raise e
				return [1, 1]

	return [1, 1]

def dfs(start_at, end_at, visited, NMatrix, cache):
	if(start_at == end_at):
		return 1 
  
	if visited[start_at] == 0:
		return 0

	visited[start_at] -= 1

	count = 0
	try:
		if start_at in NMatrix:
			for ch in NMatrix[start_at].keys():
				if visited[ch] > 0:
					if (ch,end_at) in cache:
						#print("Using cache")
						count += cache[(ch, end_at)]
					else:
						count += dfs(ch, end_at, visited, NMatrix, cache)
	except Exception as e:
		print(start_at)
		raise e
	visited[start_at] += 1
	cache[(start_at, end_at)] = 1
	return count

def augnment_graph(D, PRESERVATION):
	pass

def dfs2(start_at, end_at, visited, NMatrix, cache, PRESERVATION):

	def get_preservation(name):
		if name in PRESERVATION:
			return PRESERVATION[name]
		else:
			return 1, 1

	pr = get_preservation(start_at)
	if pr[0] >  1:
		# Notify a dispatcher
		print(start_at, pr)
	if(start_at == end_at):
		preservation = get_preservation(end_at)
		#print(preservation)
		return 1, *preservation 
  
	if visited[start_at] == 0:
		return 0, 0, 0

	visited[start_at] -= 1

	counts = [0, 0 ,0]
	try:
		if start_at in NMatrix:
			for ch in NMatrix[start_at].keys():
				if visited[ch] > 0:
					if (ch,end_at) in cache:
						#print("Using cache")
						#cache[(ch, end_at)]
						counts[0] += cache[(ch, end_at)][0]
						counts[1] += cache[(ch, end_at)][1]
						counts[2] += cache[(ch, end_at)][2]
					else:
						partial_result = dfs2(ch, end_at, visited, NMatrix, cache, PRESERVATION)
						#pr = get_preservation(ch)
						#print(partial_result, start_at, pr, ch)
						# it is the combination of
						counts[0] += partial_result[0]
						counts[1] += pr[0]*partial_result[1]
						counts[2] += pr[1]*partial_result[2]
	except Exception as e:
		print(start_at)
		raise e
	visited[start_at] += 1
	cache[(start_at, end_at)] = counts
	return counts

def get_graph_from_neo4j(result):
	EDGES = {}
	nodes = set()
	EDGES_COUNT = 0
	result = list(result)

	# print(len(result))
	for r in result:
		fr = r['start']['name']
		to = r['end']['name']

		if fr not in EDGES:
			EDGES[fr] = {}
		
		if fr == to:
			continue
		EDGES[fr][to] = 1
		
		EDGES_COUNT += 1
		nodes.add(fr)
		nodes.add(to)

	sanitized = set()

	for n in nodes:
		if n.endswith("_entry") or n.endswith("_end"):
			continue
		fname = n
		fname = n.replace("_original", "")
		fname = re.sub(r"_\d+_$", "", fname)
		fname = re.sub(r"\.\d+$", "", fname)
		sanitized.add(fname)

	# print(sanitized)
	return EDGES, nodes, EDGES_COUNT, sanitized


def create_graph_from_trace(trace, fmap):
	EDGES = {}
	nodes = set()
	EDGES_COUNT = 0

	START=None
	for t in range(1,len(trace)):
		curr = trace[t]
		prev = trace[t-1]


		ffrom = fmap[prev]['parent']
		fto = fmap[curr]['parent']

		if START is None:
			START=ffrom



		if ffrom not in EDGES:
			EDGES[ffrom] = {}
		
		#if fto == fto:
		#	continue

		EDGES[ffrom][fto] = 1
		
		EDGES_COUNT += 1
		nodes.add(ffrom)
		nodes.add(fto)
	END = fto
	# print(sanitized)
	return EDGES, nodes, EDGES_COUNT, START, END

def classify_variants_based_on_preservation(fmap, reversed, preservation):
	PRESERVATION = {}
	PROJECTION_REVERSED = {}
	for k, fname in fmap.items():
		_,N = get_preservation_for_function(preservation, fname['parent'])
		if fname['parent'] not in PRESERVATION:
			PRESERVATION[fname['parent']] = N
		
		if PRESERVATION[fname['parent']] > 0:
			PRESERVATION[fname['parent']] -= 1
			PROJECTION_REVERSED[k] = k
		else:
			PROJECTION_REVERSED[k] = reversed[fname['parent']]['group'] # the equivalence class for this variant is the parent one
	

	f = open("out/projection.json", 'w')
	f.write(json.dumps(PROJECTION_REVERSED, indent=4))
	f.close()

	return PROJECTION_REVERSED

	

def get_entropy(data, ngramsize=1):

	FREQ = {}
	for p in data:
		if p not in FREQ:
			FREQ[p] = 0
		FREQ[p] += 1
	
	PROBS = {}

	SUM = sum([v for k, v in FREQ.items()])

	for p in FREQ.keys():
		PROBS[p] = FREQ[p]/len(data)
	
	E = 0

	# print(PROBS, len(data), SUM, len(PROBS))
	for p in PROBS:
		E += -1*PROBS[p]*log(PROBS[p], 10) #32 bits per function id
	
	BEST_CASE = [1/len(data) for _ in range(len(data))]
	BE = 0
	for p in BEST_CASE:
		BE += -1*p*log(p, 10) #32 bits per function id
	

	RI = len(data)
	print(E, BE, E/BE)
	#print(E, E/log(RI, 2))
	return E, E/log(RI, 10)

import zlib

def get_entropy_by_compression(data):

	bytes = data.__str__().encode()
	
	size = len(bytes)
	#print(size)

	compressed_data = zlib.compress(bytes)
	#print()
	# compressings

	E = len(compressed_data)/len(bytes)
	#print(f"{100-100*E:.2f}%", f"{100*E:.2f}%")

	return E

# this will provide the original CG
def parse_edges(file, fmap, reversed, start_at="sodium_bin2base64"):
	content = open(file, 'r')
	edges = {}
	buffer = []
	pieces = {}
	s1 = None
	for l in content:
		if not l.startswith("->"): # it is a parent

			s = l.strip()
			if s1 is None:
				s1 = s
				continue
			
			pieces[s1] = [*buffer] # piece of a graph
			buffer = []
			s1 = s
		else:
			buffer.append(l.replace("->", "").strip())
		
	
	
	def dfs(start_at, indent = 0):
		
		if start_at in reversed:
			print("\t"*indent, start_at)
			for ch in pieces[start_at]:
				#print("\t"*(indent + 1), ch)
				if  start_at != ch:
					dfs(ch, indent + 1)
				else:
					print("\t"*indent, f"{start_at}->{ch}")

	dfs(start_at)
	return pieces

def create_graph_from_wasm(wasmfile, fname="sodium_bin2base64", blacklist=['discriminate', '_cb71P5H47J3A']):
	FUNC_START=re.compile(r"\(func \$")

	content = open(wasmfile, 'r').read()
	print("reading wat file")

	CG4FUNCTION = {}
	PATHS = {}
	LOOPS = {}
	for m in FUNC_START.finditer(content):
		start_at = m.span()[0]


		PARCOUNT = 1
		FUNCTION_CONTENT = ''	
		for c in content[start_at + 1:]:
			if c == '(':
				PARCOUNT += 1
			if c == ')':
				PARCOUNT -= 1
			
			if PARCOUNT == 0:
				break
			FUNCTION_CONTENT += c
		FUNCTION_CONTENT = FUNCTION_CONTENT.split("\n")
		FNAME = FUNCTION_CONTENT[0].split(" ")[1][1:]
		if FNAME not in CG4FUNCTION:
			CG4FUNCTION[FNAME] = {}
		if FNAME not in PATHS:
			PATHS[FNAME] = []
		for i, instr in enumerate(FUNCTION_CONTENT):
			if i == 0:
				continue
			#print(instr)
			if "call" in instr:
				# print(instr)
				instr = instr.strip()
				F2 = instr.split(" ")[1][1:]

				if F2 not in CG4FUNCTION:
					CG4FUNCTION[F2] = {}
				
				CG4FUNCTION[FNAME][F2] = {}
				if F2 != FNAME:
					PATHS[FNAME].append(F2)
				if F2 == FNAME:
					LOOPS[FNAME] = 1
				# look for far most loop
				LOOPINDEX=-1
				for j in range(i, 0, -1):
					if 'loop' in FUNCTION_CONTENT[j]:
						LOOPINDEX = j
						break
				if LOOPINDEX != -1:
					# create and edge between f2 and F but passing through other function calls in the middle
					#print(LOOPINDEX)
					CG4FUNCTION[F2][F2] = {}
					LOOPS[F2] = 1
			if "call_indirect" in instr:
				print(f"WARNING: Indirect call {instr}")
		# print(CG4FUNCTION[FNAME])
	visited = {}
	filtered = {}

	#print(CG4FUNCTION)

	def dfs2(init, chs, indent = 0):
		if init in visited or init in blacklist:
			return
		print("|","\t"*indent, init, end = "")

		visited[init] = 1
		if init in LOOPS:
			print(" <-")
		else:
			print()
		for ch in chs:
			if ch in PATHS:
				dfs2(ch, PATHS[ch], indent + 1)

	print(PATHS)
	def dfs(ed, start_at):
		if start_at in visited:
			return
		
		visited[start_at] = 1
		for ch in ed[start_at].keys():
			
			print(f"{start_at} -> {ch}")
			if ch not in visited:
				dfs(ed, ch)
	dfs2(fname, PATHS[fname])
	return CG4FUNCTION