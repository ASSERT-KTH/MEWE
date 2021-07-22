from neo4j import GraphDatabase
import os
import sys
import re
import json

from utils.utils import *
from utils.dbutils import DBUtils


class CallEdge:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, node1, node2, tpe):
		with self.driver.session() as session:
			session.run(
				f" MATCH (n1 {{id:'{node1}'}}) "
				f" MATCH (n2 {{id:'{node2}'}}) "
				f" WITH n1, n2 "
				f" MERGE (n1)-[:{tpe}]->(n2)")
			#greeting = session.write_transaction(self._create_and_return_greeting, node1, node2, tpe)


	@staticmethod
	def _create_and_return_greeting(tx, node1, node2, tpe):

		pass

class FunctionNode:

	def __init__(self, uri, user, password):
		self.driver = GraphDatabase.driver(uri, auth=(user, password))

	def close(self):
		self.driver.close()

	def set_node(self, functionId, functionName, meta, project, tpe=""):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._create_and_return_greeting, functionId, functionName, meta, project, tpe)
		
	
	def wipe(self):
		with self.driver.session() as session:
			greeting = session.write_transaction(self._wipe)

	@staticmethod
	def _wipe(tx):
		result = tx.run(
			f"MATCH (n) detach delete n")
		print(result)

	@staticmethod
	def _create_and_return_greeting(tx, functionId, functionName, meta, project, extratpe):
		tpe = "FUNCTION"
		#if functionName in zero_map:
	#		tpe="FUNCTION_END"
		if meta is not None:
			if meta['isDispatcher']:
				tpe='DISPATCHER'
		#		if functionName in zero_map:
		#			tpe="DISPATCHER_END"

			if meta['isOriginal']:
				tpe='ORIGINAL'
		#		if functionName in zero_map:
		#			tpe="ORIGINAL_END"
			if meta['isVariant']:
				tpe="VARIANT"
		#		if functionName in zero_map:
		#			tpe="VARIANT_END"

		result = tx.run(
			f"MERGE (n:{tpe}{extratpe} {{id: '{functionId}', name: '{functionName}', project: '{project}'}})")

DEBUG=False
MAX=10029

if __name__ == "__main__":

	host = os.getenv("NEO_HOST", "bolt://localhost:7687")
	user = os.getenv("NEO_USER", "neo4j")
	pass_ = os.getenv("NEO_PASS", "test")


	fmap, reversed = parse_map(sys.argv[1]) 
	project  = sys.argv[2]
	stability_check = json.loads(open(sys.argv[3], 'r').read())

	fnames = sys.argv[4::2]
	db = DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))
	
	greeter = FunctionNode(host, user, pass_)
	greeter.wipe()
	print(len(fmap))
	PRESERVATION_CACHE = calculate_preserved_cache(stability_check)
	print(PRESERVATION_CACHE, len(PRESERVATION_CACHE))
	if not DEBUG:
		functionNames = []
		for k, v in fmap.items():
			greeter = FunctionNode(host, user, pass_)
			greeter.set_node(k, v['name'], v, project)
			greeter.close()
			#if v['name'] == "_LTcore..ops..range..RangeLTusizeGTu20asu20core..slice..index..SliceIndexLTu5bTu5dGTGT::index_mut::h9c4f94c3b03aa397":
			#	raise Exception("What!!")
			functionNames.append(v['name'])



	CC=10
	for fname in fnames:
		print(fname)
		MAX += 1
		CC += 1
		EDGES_TO = {
			
		}

		path = db.first("ams", fname)['pathraw']
		if DEBUG:
			print(len(path))
		

		CHECKED = {}
		CHECKED2 = {}

		isFirst = True

		last = None
		lastN = -1
		lastP = None
		# Create start and ending nodes

		greeter = FunctionNode(host, user, pass_)
		greeter.set_node(MAX, f"{fname}_entry", None, project, tpe="ENDPOINT")
		greeter.close()

		# Ending nodes

		greeter = FunctionNode(host, user, pass_)
		greeter.set_node(MAX + 100, f"{fname}_end", None, project, tpe="END")
		greeter.close()


		for i in range(1,len(path), 1):
			sys.stdout.write(f"\r{i}/{len(path)} edges     ")
			current = path[i]



			previous = int(path[i - 1])

			currentId = int(current)

			id1 = fmap[previous]
			id2 = fmap[currentId]

			parentId1 = id1
			parentId2 = id2

			parentIdD1 = reversed[parentId1['parent']]['group']
			parentIdD2 = reversed[parentId2['parent']]['group']

			lastP = parentIdD2
			if parentIdD1 == parentIdD2 and parentId1['isDispatcher']:

				print(current, previous, parentIdD1, parentIdD2)
				# it is a call from a dispatcher to a variant, avoid
				continue


			#if DEBUG:
		#		print(parentId2)
			# Original graph
			
			greeter = CallEdge(host, user, pass_)
			greeter.set_node(parentIdD1, parentIdD2, f"ST{CC}")
			#greeter.close()

			p1 = parentId1['parent']
			p2 = parentId2['parent']
			
			TO = [[reversed[p1]['group']],[reversed[p2]['group']]]

			# Mltivariant version
			if p1 in PRESERVATION_CACHE:
				W1,N1 = PRESERVATION_CACHE[p1] # get_preservation_for_function(stability_check, p1)
			else:
				W1, N1 = 1 , 1
			variantsF1 = [reversed[f"{p1}_{w}_"]['group'] for w in range(10000) if f"{p1}_{w}_" in reversed]

			variantsF1 += [reversed[p1]['group']] # Adding the original as well

			TO[0] = variantsF1


			if p2 in PRESERVATION_CACHE:
				W2,N2 = PRESERVATION_CACHE[p2] # get_preservation_for_function(stability_check, p1)
			else:
				W2,N2 = 1 , 1
			variantsF2 = [reversed[f"{p2}_{w}_"]['group'] for w in range(10000) if f"{p2}_{w}_" in reversed]

			variantsF2 += [reversed[p2]['group']] # Adding the original as well

			CHECKED[p2] = True
			#print(p1,W1,N2,p2, W2, N2)

			TO[1] = variantsF2

			if f"{TO}" not in CHECKED:
				last = TO
				lastN = N2
				fr, to = TO
				for n1 in fr:
					for n2 in to:
						if f"{n1},{n2}" not in CHECKED:
							greeter = CallEdge(host, user, pass_)
							greeter.set_node(n1, n2, f"MST{CC}")
							#greeter.close()
							CHECKED[f"{n1},{n2}"] = True
				for n1 in fr[:N1]: # break at the preservation
					for n2 in to[:N2]: # break at the preservation
						if f"{n1},{n2}" not in CHECKED2:
							greeter = CallEdge(host, user, pass_)
							greeter.set_node(n1, n2, f"WST{CC}")
							#greeter.close()
							CHECKED2[f"{n1},{n2}"] = True

				CHECKED[f"{TO}"] = True
				if isFirst:
					
					greeter = CallEdge(host, user, pass_)
					greeter.set_node(MAX, parentIdD1, f"ST{CC}")
					#greeter.close()

					for n2 in fr:
						greeter = CallEdge(host, user, pass_)
						greeter.set_node(MAX, n2, f"MST{CC}")
						#greeter.close()

					for n2 in fr[:N1]:
						greeter = CallEdge(host, user, pass_)
						greeter.set_node(MAX, n2, f"WST{CC}")
						#greeter.close()
					isFirst = False

		_, to = last
		
		greeter = CallEdge(host, user, pass_)
		greeter.set_node(lastP, MAX + 100 , f"ST{CC}")
		#greeter.close()

		for n2 in to:
			greeter = CallEdge(host, user, pass_)
			greeter.set_node(n2, MAX + 100, f"MST{CC}")
			#greeter.close()

		for n2 in to[:N2]:
			greeter = CallEdge(host, user, pass_)
			greeter.set_node(n2, MAX + 100, f"WST{CC}")
			#greeter.close()
		print("MCG Edges created")

