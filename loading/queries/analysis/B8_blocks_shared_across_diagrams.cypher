// B.8 Check the blocks participating in more than one diagram.
MATCH (b:BLOCK)<-[:IS_INSTANCE_OF]-(:INSTANCE)<-[:REPRESENTS]-(:LIFELINE)-[:IS_PART_OF]->(i:INTERACTION)
WITH b, collect(DISTINCT i.name) AS diagrams
WHERE size(diagrams) > 1
RETURN b.name AS block, diagrams
ORDER BY block;
