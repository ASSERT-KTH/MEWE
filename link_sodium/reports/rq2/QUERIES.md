## Get full path starting from a node, static CFG

MATCH p=(start:FUNCTION {name: 'function_name'})-[r:ST*..]->(k) return p