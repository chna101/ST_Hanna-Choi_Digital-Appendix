// B.6 Timing constraints: each DURATION hypernode with its bounds and the two events it constrains.
MATCH (dc:SD:HYPERNODE:DURATION)-[:IS_PART_OF]->(i:INTERACTION)
MATCH (e:EVENT)-[:IS_PART_OF]->(dc)
OPTIONAL MATCH (e)-[:IS_PART_OF]->(m:MESSAGE)
OPTIONAL MATCH (e)<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->(:INSTANCE)-[:IS_INSTANCE_OF]->(b)
RETURN i.name AS interaction,
       dc.min AS min, dc.max AS max,
       e.id AS event, m.name AS message, b.name AS block
ORDER BY interaction, event;
