from neo4j import GraphDatabase
import os
import sys
import re

from utils import *


class CallEdge:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, node1, node2, tpe):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._create_and_return_greeting, node1, node2, tpe)


	@staticmethod
	def _create_and_return_greeting(tx, node1, node2, tpe):

		result = tx.run(
			f" MATCH (n1 {{id:'{node1}'}}) "
			f" MATCH (n2 {{id:'{node2}'}}) "
			f" WITH n1, n2 "
			f" MERGE (n1)-[:{tpe}]->(n2)")

class FunctionNode:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, functionId, functionName, meta, project, zero_map):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._create_and_return_greeting, functionId, functionName, meta, project, zero_map)
		
	
	def wipe(self):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._wipe)

	@staticmethod
	def _wipe(tx):
		result = tx.run(
			f"MATCH (n) detach delete n")
		print(result)

	@staticmethod
	def _create_and_return_greeting(tx, functionId, functionName, meta, project, zero_map):
		tpe = "FUNCTION"
		if functionName in zero_map:
			tpe="FUNCTION_END"
		if meta['isDispatcher']:
			tpe='DISPATCHER'
			if functionName in zero_map:
				tpe="DISPATCHER_END"

		if meta['isOriginal']:
			tpe='ORIGINAL'
			if functionName in zero_map:
				tpe="ORIGINAL_END"
		if meta['isVariant']:
			tpe="VARIANT"
			if functionName in zero_map:
				tpe="VARIANT_END"

		result = tx.run(
			f"MERGE (n:{tpe} {{id: '{functionId}', name: '{functionName}', project: '{project}'}})")


if __name__ == "__main__":

	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")


	fmap, reversed = parse_functions(sys.argv[1])
	edges = parseedges(sys.argv[2])
	zero_map = get_zero_degree_functions(sys.argv[3])
	project  = sys.argv[4]

	
	greeter = FunctionNode(host, user, pass_)
	greeter.wipe()
	print(len(fmap))
	for k, v in fmap.items():
		greeter = FunctionNode(host, user, pass_)
		greeter.set_node(k, v['name'], v, project, zero_map)
		greeter.close()
		pass

	print("FUNCTION nodes created")

	EDGES_TO = {
		
	}

	print(len(edges))
	for s in edges:
		e1, e2 = s
		es1 = e1.strip()
		es2 = e2.strip()


		id1, id2 = reversed[es1], reversed[es2]

		
		greeter = CallEdge(host, user, pass_)
		greeter.set_node(id1, id2, "MST")
		greeter.close()

		# Do not insert edge for variants in the initial graph
		if fmap[id2]['isVariant']:
			continue
		greeter = CallEdge(host, user, pass_)
		greeter.set_node(id1, id2, "ST")
		greeter.close()
	
	print("MCG Edges created")

