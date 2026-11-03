// B.4 As B.3, with the enclosing combined fragment and its guard for each message.
MATCH (i:INTERACTION)
MATCH (start:MESSAGE)-[:IS_PART_OF]->(i)
WHERE NOT (:MESSAGE)-[:CONTROL_FLOW]->(start)
MATCH path = (start)-[:CONTROL_FLOW*0..]->(m:MESSAGE)
WITH i, m, min(length(path)) AS seq
OPTIONAL MATCH (se:EVENT {id:m.sendEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(sb)
OPTIONAL MATCH (:EVENT {id:m.receiveEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(rb)
OPTIONAL MATCH (se)-[:IS_PART_OF]->(op:SD:HYPERNODE:OPERAND)-[:IS_PART_OF]->(h:SD:HYPERNODE)
RETURN i.name AS interaction, seq,
       h.operator AS fragment, op.guard AS condition,
       coalesce(sb.name,'(external)') AS from,
       m.name AS message,
       coalesce(rb.name,'(lost)') AS to
ORDER BY interaction, seq;
