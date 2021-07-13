from neo4j import GraphDatabase
import os
import sys
import json
from utils import *

class CallEdge:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, node1, node2):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._create_and_return_greeting, node1, node2)


	@staticmethod
	def _create_and_return_greeting(tx, node1, node2):

		result = tx.run(
			f" MATCH (n1 {{id:'{node1}'}}) "
			f" MATCH (n2 {{id:'{node2}'}}) "
			f" WITH n1, n2 "
			f" MERGE (n1)-[:ST]->(n2)")


if __name__ == "__main__":

	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")

	static_map = sys.argv[1]
	fmap = sys.argv[2]
	project_name = sys.argv[3]

	mp, reversed = parse_map(fmap)
	static_edges = parse_static(static_map)
	
	for caller, called in static_edges:
		if caller in reversed and called in reversed:
			
			greeter = CallEdge(host, user, pass_)

			greeter.set_node(reversed[caller]['group'], reversed[called]['group'])
			greeter.close()
			print(caller, called)
	
	print("Static map created")