// B.9 Check every message involving the xxx across all diagrams.
// change xxx to the name of block to be checked
MATCH (b:BLOCK {name:'OBC'})<-[:IS_INSTANCE_OF]-(:INSTANCE)<-[:REPRESENTS]-(ll:LIFELINE)-[:IS_PART_OF]->(i:INTERACTION)
MATCH (ll)-[:COVERS]->(e:EVENT)-[:IS_PART_OF]->(m:MESSAGE)
WITH i, m
RETURN i.name AS interaction,
       count(m) AS obc_exchanges,
       collect(m.name) AS messages
ORDER BY interaction;
