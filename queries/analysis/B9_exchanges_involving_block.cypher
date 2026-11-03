// B.9 Check every message involving the xxx across all diagrams.
// change xxx to the name of block to be checked
MATCH (b:BLOCK {name:'xxx'})<-[:IS_INSTANCE_OF]-(:INSTANCE)<-[:REPRESENTS]-(ll:LIFELINE)-[:IS_PART_OF]->(i:INTERACTION)
MATCH (ll)-[:COVERS]->(e:EVENT)-[:IS_PART_OF]->(m:MESSAGE)
RETURN i.name AS interaction, count(DISTINCT m) AS obc_exchanges
ORDER BY interaction;
