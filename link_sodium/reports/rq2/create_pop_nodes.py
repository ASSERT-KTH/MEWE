from neo4j import GraphDatabase
import os
import sys
import json

from utils import *

class PopNode:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def set_node(self, popname):
        with self.driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, popname)

    @staticmethod
    def _create_and_return_greeting(tx, popname):
        result = tx.run(
            f"MERGE (n:POP {{id: '{popname}'}})")


if __name__ == "__main__":

    host = os.getenv("NEO_HOST", "bolt://localhost:7687")
    user = os.getenv("NEO_USER", "neo4j")
    pass_ = os.getenv("NEO_PASS", "test")


    pops = json.loads(open(sys.argv[1], 'r').read())

    for v in pops:
        greeter = PopNode(host, user, pass_)
        greeter.set_node(v['code'])
        greeter.close()

    print("POPs created")