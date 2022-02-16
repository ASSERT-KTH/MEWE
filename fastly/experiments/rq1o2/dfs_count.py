from utils.utils import *
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

if __name__ == "__main__":
	
	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")
	stability_check = json.loads(open(sys.argv[1], 'r').read())

	PREVIOUS_ALL = -1
	for fname, tpe in zip(sys.argv[2::2], sys.argv[3::2]):

		PREVIOUS = -1
		for tp in ['ST', 'MST', 'WST']:
		#print(f"## {tp}")
			#print("Getting CG for", tp, tpe)
			gr = EdgeQuery(host, user, pass_)
			subgraph, cyclomatic = gr.set_node(fname, f"{tp}{tpe}")
			gr.close()

			#print("Projecting graph for DFS", tp)
			D, nodes, edges, sanitized = get_graph_from_neo4j(subgraph)
			
			visited = dict(
				zip(nodes, [REVISIT_COUNT for _ in nodes])
			)
			#print("Executing DFS", tp, len(visited), edges)

			CACHE = {}

			#print(f'{fname}_entry', f'{fname}_end')
			#open("t.json", "w").write(json.dumps(D, indent=4))

			COUNT = dfs(f'{fname}_entry', f'{fname}_end', visited, D, CACHE)


			print(f"| {fname} |  {COUNT} ", end="")
			if PREVIOUS > -1:
				print(f" | {COUNT/PREVIOUS:.2f}")
			else:
				print("|")

			SUM = [0, 0]
			MULT = [1, 1]
			if tp != 'ST' and PRINT_INVOLVED:
				for f in sanitized:
					W1,N1 = get_preservation_for_function(stability_check, f)
					if W1 > 1: # It has more than 1 variant
						print(f, W1, N1)
						SUM[0] += W1
						SUM[1] += N1
						MULT[0] *= W1
						MULT[1] *= N1
				print(SUM[0], MULT[0])
				print(SUM[1], MULT[1])
				print()

			PREVIOUS = COUNT
		print()