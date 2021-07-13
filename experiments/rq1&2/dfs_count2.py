from utils.utils import *
from utils.dbutils import DBUtils

import os
from neo4j import GraphDatabase
import os
import sys
import re
import json

db = DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))


class EdgeQuery:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, fname, tpe):
		with self.driver.session() as session:
			subpgrah = session.run(f"MATCH p=(start)-[r:{tpe}]->(end) return start,end").data()
 #session.read_transaction(self._create_and_return_greeting, fname, tpe)
			# cyclomatic = session.read_transaction(self._get_cyclomatic, fname, tpe)

			return subpgrah,None

	@staticmethod
	def _create_and_return_greeting(tx, tpe):
		# print(f"MATCH p=(start {{name:'{fname}_entry'}})-[:{tpe}*]->(k {{name: '{fname}_end'}}) return count(p) as count")
		c  = tx.run(f"MATCH p=(start)-[r:{tpe}]->(end) return start,end")
		return c

	@staticmethod
	def _get_cyclomatic(tx, fname, tpe):
		c = tx.run(f"match p=(k)-[:{tpe}]->(n) unwind nodes(p) as nodes return count(distinct(nodes)) as N")

		N = 0
		for line in c:
			N = line['N']
			break
		c = tx.run(f"match p=(k)-[:{tpe}]->(n) unwind p as paths return count(distinct(paths)) as E")
		E = 0
		for line in c:
			E = line['E']
			break

		# print(N, E)
		return (N, E)

PRINT_INVOLVED = False
REVISIT_COUNT=1

def get_trace_based_ontype(type, file):
	if type == "db":
		return lambda x: db.first("bma", x)["pathraw"]
	if type == "file":
		return lambda f: json.loads(open(file, 'r').read())[f]['instrumentedPureRandom']['paths']['bma'][0]['path']


'''
_ZN5alloc5alloc6Global10alloc_impl17h1f328160f76f12cfE 167
_ZN60_$LT$qrcode..types..Mode$u20$as$u20$core..cmp..PartialEq$GT$2eq17ha263fa5e4af74859E 19
_ZN56_$LT$i16$u20$as$u20$checked_int_cast..CheckedIntCast$GT$16as_usize_checked17hf8c27e538d0e444fE 428
_ZN4core10intrinsics19copy_nonoverlapping17hd9866c2fcb327602E 5
_ZN58_$LT$usize$u20$as$u20$checked_int_cast..CheckedIntCast$GT$14as_u16_checked17h8c652c149b1ec8f1E 2
_ZN5alloc7raw_vec19RawVec$LT$T$C$A$GT$16with_capacity_in17hc167591bf67cc4c3E 3
_ZN4core4iter6traits8iterator8Iterator8for_each17h03b17951018b3e39E 22
_ZN5alloc7raw_vec19RawVec$LT$T$C$A$GT$11allocate_in17h344cc4811a228da3E 16
_ZN77_$LT$alloc..raw_vec..RawVec$LT$T$C$A$GT$$u20$as$u20$core..ops..drop..Drop$GT$4drop17h2653c8de238d7e6bE 11
_ZN6qrcode6canvas6Canvas20draw_finder_patterns17hdd8f6522c27cb362E 43
_ZN6qrcode6canvas6Canvas15coords_to_index17h392521962941e573E 397
_ZN6qrcode6canvas14mask_functions16horizontal_lines17h0c5de493f21ce1a3E 310
_ZN4core4iter6traits8iterator8Iterator4fold17had50487807a5fe23E 282
_ZN77_$LT$alloc..raw_vec..RawVec$LT$T$C$A$GT$$u20$as$u20$core..ops..drop..Drop$GT$4drop17h7425ee577f6364a4E 10
_ZN4core6option15Option$LT$T$GT$3map17h1a47d23c8837b815E 298
'''
if __name__ == "__main__":
	
	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")
	stability_check = json.loads(open(sys.argv[1], 'r').read())
	fmap, reversed = parse_map(sys.argv[2])
	trace_type=sys.argv[3]

	fromargv = 4
	fl = None
	if trace_type == "file":
		fl = sys.argv[4]
		fromargv = 5

	PREVIOUS_ALL = -1
	PRESERVATION_CACHE = calculate_preserved_cache(stability_check)

	for fname in sys.argv[fromargv::2]:

		PREVIOUS = -1
		trace =  get_trace_based_ontype(trace_type, fl)(fname)
		#print(f"## {tp}")
	
		D, nodes, edges, start, end = create_graph_from_trace(trace, fmap)
		#print(D, start, end)
		
		visited = dict(
			zip(nodes, [REVISIT_COUNT for _ in nodes])
		)
		#print("Executing DFS", tp, len(visited), edges)

		CACHE = {}

		#print(f'{fname}_entry', f'{fname}_end')
		#open("t.json", "w").write(json.dumps(D, indent=4))

		COUNTS = dfs2(start, end, visited, D, CACHE, PRESERVATION_CACHE)


		print(f"| {fname} |  {COUNTS[0]} ")
		print(f"|         |  {COUNTS[1]} | {COUNTS[1]/COUNTS[0]:.2f}")
		print(f"|         |  {COUNTS[2]} | {COUNTS[2]/COUNTS[1]:.2f}")
		#if PREVIOUS > -1:
	#		print(f" | {COUNT/PREVIOUS:.2f}")
	#	else:
	#		print("|")

		SUM = [0, 0]
		MULT = [1, 1]
		#if tp != 'ST' and PRINT_INVOLVED:
	#		for f in sanitized:
			#	W1,N1 = get_preservation_for_function(stability_check, f)
			#	if W1 > 1: # It has more than 1 variant
			#		print(f, W1, N1)
			#		SUM[0] += W1
			#		SUM[1] += N1
			#		MULT[0] *= W1
			#		MULT[1] *= N1
			#print(SUM[0], MULT[0])
			#print(SUM[1], MULT[1])
			#print()

			#PREVIOUS = COUNT
		print()