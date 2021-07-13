from neo4j import GraphDatabase
import os
import sys
import json

EDGES =  set()

class CallEdge:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, node1, node2, pop, func, dispatcher,project, time=0):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._create_and_return_greeting, node1, node2, pop, func, time, dispatcher, project)


	@staticmethod
	def _create_and_return_greeting(tx, node1, node2, pop, func, time, dispatcher, project):

		k = f"{node1}{node2}{pop}{func}{dispatcher}"

		if k not in EDGES:
			result = tx.run(
				f" MATCH (n1 {{id:'{node1}'}}) "
				f" MATCH (n2 {{id:'{node2}'}}) "
				f" WITH n1, n2 "
				f" MERGE (n1)-[:CLL {{function:'{func}', pop:'{pop}', dispatcher:'{dispatcher}', pathid:'{time}', project: '{project}'}}]->(n2)")
			EDGES.add(k)


if __name__ == "__main__":

	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")

	data = json.loads(open(sys.argv[1], 'r').read())
	function_name = sys.argv[2]
	dispatcher_type = sys.argv[3]
	project = sys.argv[4]

	d = data[function_name][dispatcher_type]

	paths = d['paths']
	for pop in paths:
		poppaths = paths[pop]

		for pathdict in poppaths:
			path = pathdict['path']
			# entrypoint
			greeter = CallEdge(host, user, pass_)
			greeter.set_node(pop.upper(), path[0], pop, function_name, dispatcher_type, project)
			greeter.close()

			for i,n1 in enumerate(path[:-1]):
				greeter = CallEdge(host, user, pass_)
				greeter.set_node(n1, path[i + 1], pop, function_name, dispatcher_type, project, i)
				greeter.close()

	
	print("Edges created")