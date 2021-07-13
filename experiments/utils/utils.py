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

	if(start_at == end_at):
		preservation = get_preservation(end_at)
		#print(preservation)
		return 1, *preservation 
  
	if visited[start_at] == 0:
		return 0, 0, 0

	visited[start_at] -= 1

	pr = get_preservation(start_at)
	if pr[1] >  1:
		# Notify a dispatcher
		print(start_at, pr)
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

	for p in FREQ:
		PROBS[p] = FREQ[p]/len(data)
	
	E = 0

	for p in PROBS:
		E += -1*PROBS[p]*log(PROBS[p], 2) #32 bits per function id
	
	RI = len(PROBS.keys())
	#print(E, E/log(RI, 2))
	return E, E/log(RI, 2)

import zlib

def get_entropy_by_compression(data):

	bytes = functools.reduce(lambda x, y: x + y.to_bytes(4, 'big'), data, b'')
	
	size = len(bytes)
	#print(size)

	compressed_data = zlib.compress(bytes)
	#print()
	# compressings

	E = len(compressed_data)/len(bytes)
	#print(f"{100-100*E:.2f}%", f"{100*E:.2f}%")

	return E

if __name__ == "__main__":

	import json
	import sys
	'''
	from utils.dbutils import DBUtils
	import os


	fmap, reversed = parse_map(sys.argv[1])
	preservation = json.loads(open(sys.argv[2], 'r').read())
	db = DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

	trace = db.first("bma", "run_qr")["pathraw"]
	EDGES, nodes, EDGES_COUNT, START, END = create_graph_from_trace(trace, fmap)
	print(EDGES, nodes, EDGES_COUNT, START, END)
	'''

	paths = json.loads(open(sys.argv[1], 'r').read())
	fname = sys.argv[2]

	
	p = paths[fname]['instrumentedPureRandom']['paths']
	overall = []

	r = 2
	t = []
	for i in range(100):
		try:
			for pop, k in p.items():
				overall += k[i]['path']
		except Exception as e:
			print(e, pop)
			pass
	print(len(overall))
	# overall = [1,2,2,1]
	entropy = get_entropy(overall)
	# entropy = get_entropy_by_compression(overall)


	import matplotlib.pyplot as plt

	plt.scatter([
		0.007549822026078572, 0.004562478418211799, 0.01138211298827306, 0.0035073945050326815, 0.003529551127067959
	], [
		12314, 253, 41, 2538, 78
	])
	#plt.show()
# 
# crypto_core_ed25519_scalar_random 0.79273131273825 0.007549822026078572 12314
# crypto_aead_chacha20poly1305_ietf_encrypt_detached 0.3011235756019788 0.004562478418211799 253
# bin2base640.4325202935543763 0.01138211298827306 41
# crypto_core_ed25519_scalar_invert 0.2805915604026145 0.0035073945050326815 2538
