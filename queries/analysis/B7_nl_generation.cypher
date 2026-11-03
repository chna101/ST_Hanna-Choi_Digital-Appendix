// B.7 Natural-language generation per message: one controlled requirement statement per exchange,
// with the governing fragment operator and guard as the condition, and the timing bound appended
// when the message is covered by a duration constraint.
MATCH (i:INTERACTION)
MATCH (start:MESSAGE)-[:IS_PART_OF]->(i)
WHERE NOT (:MESSAGE)-[:CONTROL_FLOW]->(start)
MATCH path = (start)-[:CONTROL_FLOW*0..]->(m:MESSAGE)
WITH i, m, min(length(path)) AS seq
OPTIONAL MATCH (se:EVENT {id:m.sendEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(sb)
OPTIONAL MATCH (:EVENT {id:m.receiveEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(rb)
OPTIONAL MATCH (se)-[:IS_PART_OF]->(op:SD:HYPERNODE:OPERAND)-[:IS_PART_OF]->(h:SD:HYPERNODE)
OPTIONAL MATCH (dc:SD:HYPERNODE:DURATION)<-[:IS_PART_OF]-(cn) WHERE cn.id = m.id
WITH i, seq, m, sb, rb, op, h, head(collect(DISTINCT dc)) AS dc
RETURN i.name AS interaction, seq,
       'The ' + coalesce(sb.name,'external source') +
       " shall send '" + m.name + "' to the " + coalesce(rb.name,'(lost)') +
       CASE WHEN op.guard IS NULL OR op.guard = '' THEN ''
            ELSE ' (' + h.operator + ': ' + op.guard + ')' END +
       CASE WHEN dc IS NULL THEN ''
            WHEN dc.max IS NULL OR dc.max = '' THEN ' within ' + dc.min
            ELSE ' within ' + dc.min + ' to ' + dc.max END +
       '.' AS requirement
ORDER BY interaction, seq;
