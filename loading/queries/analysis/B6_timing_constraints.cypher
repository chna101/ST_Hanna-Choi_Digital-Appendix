// B.6 Timing constraints: each DURATION hypernode with its bounds and the two events it constrains.
MATCH (dc:SD:HYPERNODE:DURATION)-[:IS_PART_OF]->(i:INTERACTION)
MATCH (e:EVENT)-[:IS_PART_OF]->(dc)
RETURN i.name AS interaction, dc.min AS min, dc.max AS max,
       collect(e.id) AS constrained_events;
