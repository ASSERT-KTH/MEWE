from neo4j import GraphDatabase
import os
import sys
import re
import json

from utils import *


class EdgeQuery:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, fname, tpe):
		with self.driver.session() as session:
			paths = session.read_transaction(self._create_and_return_greeting, fname, tpe)
			cyclomatic = session.read_transaction(self._get_cyclomatic, fname, tpe)

			return paths,cyclomatic

	@staticmethod
	def _create_and_return_greeting(tx, fname, tpe):
		# print(f"MATCH p=(start {{name:'{fname}_entry'}})-[:{tpe}*]->(k {{name: '{fname}_end'}}) return count(p) as count")
		c = tx.run(f"MATCH p=(start {{name:'{fname}_entry'}})-[:{tpe}*]->(k {{name: '{fname}_end'}}) return count(p) as count")

		for line in c:
			return line['count']

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

if __name__ == "__main__":

	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")

	for tp in ['ST', 'MST', 'WST']:
		print(f"## {tp}")
		for fname, tpe in zip(sys.argv[1::2], sys.argv[2::2]):
			gr = EdgeQuery(host, user, pass_)
			a = gr.set_node(fname, f"{tp}{tpe}")
			# name, 
			Cyclomatic = a[1][1] - a[1][0] + 2
			# nodes, edges, cyclomatic, paths
			print(f"| {fname} | {a[1][0]} | {a[1][1]} |{Cyclomatic} | {a[0]} |")
			gr.close()