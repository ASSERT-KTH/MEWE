import matplotlib.pyplot as plt

import matplotlib
from math import sqrt
SPINE_COLOR = 'gray'
# print(plt.style.available)
plt.style.use('seaborn-colorblind')
import re

tick_y_size = 8
tick_x_size = 8
title_size = 12

def latexify(fig_width=None, fig_height=None, columns=1, font_size=8, tick_size=8):
	"""Set up matplotlib's RC params for LaTeX plotting.
	Call this before plotting a figure.

	Parameters
	----------
	fig_width : float, optional, inches
	fig_height : float,  optional, inches
	columns : {1, 2}
	"""

	# code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

	# Width and max height in inches for IEEE journals taken from
	# computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

	#assert(columns in [1,2])

	if fig_width is None:
		fig_width = 3.7 if columns==1 else 6.9 # width in inches

	if fig_height is None:
		golden_mean = (sqrt(5)-1.0)/2.0	# Aesthetic ratio
		fig_height = fig_width*golden_mean + 1.2 # height in inches

	#if fig_height > MAX_HEIGHT_INCHES:
	print(f"WARNING: fig_height too large: {fig_height}.")
	#print(matplotlib.rcParams.keys())
	pgf_with_latex = {					  # setup matplotlib to use latex for output
		"pgf.texsystem": "pdflatex",		# change this if using xetex or lautex
		"text.usetex": True,				# use LaTeX to write all text
		"font.family": "serif",
		"font.serif": [],				   # blank entries should cause plots
		"font.monospace": [],
		"axes.labelsize": font_size,			   # LaTeX default is 10pt font.
		"font.size": font_size,
		"legend.fontsize": font_size,			   # Make the legend/label fonts
		"xtick.labelsize": tick_size,			   # a little smaller
		"ytick.labelsize": tick_size,
		"figure.figsize": [fig_width, fig_height],	 # default fig size of 0.9 textwidth
		#"pgf.preamble": [
		#	r"\\usepackage[utf8x]{inputenc}",	# use utf8 fonts
		#	r"\\usepackage[T1]{fontenc}",		# plots will be generated
		#	r"\\usepackage[detect-all,locale=DE]{siunitx}",
		#	]								   # using this preamble
		}

	matplotlib.rcParams.update(pgf_with_latex)


def format_axes(ax, hide = ['top', 'right'], show= ['left', 'bottom']):

	for spine in hide:
		ax.spines[spine].set_visible(False)

	for spine in show:
		ax.spines[spine].set_color(SPINE_COLOR)
		ax.spines[spine].set_linewidth(0.5)

	ax.xaxis.set_ticks_position('bottom')
	ax.yaxis.set_ticks_position('left')

	for axis in [ax.xaxis, ax.yaxis]:
		axis.set_tick_params(direction='out', color=SPINE_COLOR)

	return ax


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
		meta = {}

		if fname.endswith("_original"):
			meta['isOriginal'] = True
			originals.add(fname.replace("_original", ""))

	print(originals)
	for line in lines:
		fname, id = line.split(",")
		meta = {}

		meta['parent'] = re.sub(r"\.\d+", "", fname)
		meta['parent'] = re.sub(r"(.*)_\d+_", "", meta['parent'])
		meta['parent'] = meta['parent'].replace("_original", "")
		
		if fname.endswith("_original"):
			meta['isOriginal'] = True
			originals.add(fname.replace("_original", ""))
		else:
			meta['isOriginal'] = False

		if re.sub(r"\.\d+", "", fname) in originals: # may be a dispatcher
			meta['isDispatcher'] = True
		else:
			meta['isDispatcher'] = False

		if re.compile(r"(.*)_\d+_").match(fname): # is a variant
			print("Variant", fname)
			meta['isVariant'] = True
		else:
			meta['isVariant'] = False

		meta['name'] = fname
		result[int(id)] = meta
		reversed[fname] = {
			'group': int(id)
		}

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

def get_preservation_for_function(resultjson, fname):

	for k, v in resultjson.items():
		if 'functions' in v and fname in v['functions']:
			try:
				c = sum([1 if p[0]['isPreserved'] else 0 for p in v['pairs']])
				t = len(v['pairs'])
			
				#print(fname, t, c)
				return [t, c]
			except Exception as e:
				#print(e)
				return [1, 1]

	return [1, 1]

def dfs(start_at, end_at, visited, NMatrix, cb):
	if(start_at == end_at):
		cb()
		return 
  
	if visited[start_at] == 0:
		return

	visited[start_at] -= 1

	for ch in NMatrix[start_at].keys():
		if visited[ch] > 0:
			dfs(ch, end_at, visited, NMatrix, cb)
   
	visited[start_at] += 1
	return

def get_graph_from_neo4j(result):
	EDGES = {}
	nodes = set()
	EDGES_COUNT = 0
	for r in result:
		fr = r['paths']._relationships[0].nodes[0]['name']
		to = r['paths']._relationships[0].nodes[1]['name']

		if fr not in EDGES:
			EDGES[fr] = {}
		
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
		fname = re.sub(r"_\d+_", "", fname)
		fname = re.sub(r"\.\d+", "", fname)
		sanitized.add(fname)

	# print(sanitized)
	return EDGES, nodes, EDGES_COUNT, sanitized