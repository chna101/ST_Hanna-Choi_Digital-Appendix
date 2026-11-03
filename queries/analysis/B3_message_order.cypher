// B.3 Message order per interaction, recovered by traversing the CONTROL_FLOW chain;
// sender and receiver via COVERS and REPRESENTS.
MATCH (i:INTERACTION)
MATCH (start:MESSAGE)-[:IS_PART_OF]->(i)
WHERE NOT (:MESSAGE)-[:CONTROL_FLOW]->(start)
MATCH path = (start)-[:CONTROL_FLOW*0..]->(m:MESSAGE)
WITH i, m, min(length(path)) AS seq
OPTIONAL MATCH (:EVENT {id:m.sendEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(sb)
OPTIONAL MATCH (:EVENT {id:m.receiveEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(rb)
RETURN i.name AS interaction, seq,
       coalesce(sb.name,'(external)') AS from,
       m.name AS message,
       coalesce(rb.name,'(lost)') AS to,
       CASE WHEN m:LOST THEN 'lost' WHEN m:FOUND THEN 'found' ELSE 'normal' END AS kind
ORDER BY interaction, seq;
