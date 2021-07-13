from utils import *
import os
from neo4j import GraphDatabase
import os
import sys
import re
import json

class EdgeQuery:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, fname, tpe):
		with self.driver.session() as session:
			subpgrah = 	session.run(f"MATCH p=(start)-[:{tpe}]->(k) unwind p as paths return paths")
 #session.read_transaction(self._create_and_return_greeting, fname, tpe)
			cyclomatic = session.read_transaction(self._get_cyclomatic, fname, tpe)

			return subpgrah,cyclomatic

	@staticmethod
	def _create_and_return_greeting(tx, fname, tpe):
		# print(f"MATCH p=(start {{name:'{fname}_entry'}})-[:{tpe}*]->(k {{name: '{fname}_end'}}) return count(p) as count")

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
# generate metadata for https://sketchviz.com/new
if __name__ == "__main__":
	
	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")
	stability_check = json.loads(open(sys.argv[1], 'r').read())

	PREVIOUS_ALL = -1
	NODES = []
	E = []
	for fname, tpe in zip(sys.argv[2::2], sys.argv[3::2]):

		PREVIOUS = -1
		for tp in ['ST', 'MST', 'WST']:
		#print(f"## {tp}")

			gr = EdgeQuery(host, user, pass_)
			subgraph, cyclomatic = gr.set_node(fname, f"{tp}{tpe}")
			gr.close()

			D, nodes, edges, sanitized = get_graph_from_neo4j(subgraph)
			
			visited = dict(
				zip(nodes, [REVISIT_COUNT for _ in nodes])
			)
			COUNT = 0

			for k in D.keys():
				for k2 in D[k].keys():
					if k not in NODES:
						NODES.append(k)
					if k2 not in NODES:
						NODES.append(k2)
					
					i1 = NODES.index(k)
					i2 = NODES.index(k2)
					if f"{i1} -> {i2}" not in E:
						print(f"{i1} -> {i2}")
						E.append(f"{i1} -> {i2}")
		print()