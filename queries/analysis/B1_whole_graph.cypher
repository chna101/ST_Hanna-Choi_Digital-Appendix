// B.1 Whole-graph view: returns every node and relationship,
// used to render the complete graph of a model in the Neo4j Browser.
MATCH (n)
OPTIONAL MATCH (n)-[r]-(m)
RETURN n, r, m;
