// B.14 TMBR natural language per interaction and mode: one requirement statement per mode,
// weaving the ordered messages. The operator maps to a verb (loop -> repeatedly,
// break -> abort and, par -> concurrently); par messages are joined with "and" rather
// than "then"; and a message covered by a duration constraint carries its timing bound.
MATCH (i:INTERACTION)
MATCH (start:MESSAGE)-[:IS_PART_OF]->(i)
WHERE NOT (:MESSAGE)-[:CONTROL_FLOW]->(start)
MATCH gp = (start)-[:CONTROL_FLOW*0..]->(msg:MESSAGE)
WITH i, msg, min(length(gp)) AS pos
MATCH (mode:STATE)<-[:IS_PART_OF]-(top:SD:HYPERNODE) WHERE top.operator IS NOT NULL
MATCH (frag:SD:HYPERNODE)-[:IS_PART_OF*0..]->(top) WHERE frag.operator IS NOT NULL
MATCH (frag)<-[:IS_PART_OF]-(op:SD:HYPERNODE:OPERAND)<-[:IS_PART_OF]-(se:EVENT)-[:IS_PART_OF]->(msg)
WHERE se.id = msg.sendEvent
OPTIONAL MATCH (se)<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(sb)
OPTIONAL MATCH (:EVENT {id:msg.receiveEvent})<-[:COVERS]-(:LIFELINE)-[:REPRESENTS]->()-[:IS_INSTANCE_OF]->(rb)
OPTIONAL MATCH (dc:SD:HYPERNODE:DURATION)<-[:IS_PART_OF]-(cn) WHERE cn.id = msg.id
WITH i, mode, frag, op, msg, sb, rb, pos, head(collect(DISTINCT dc)) AS dc
ORDER BY pos
WITH i.name AS interaction, mode.name AS mode, frag.operator AS fragment, op.guard AS guard,
     collect("send '" + msg.name + "' from " + coalesce(sb.name,'the system') + " to " + coalesce(rb.name,'(lost)') +
             CASE WHEN dc IS NULL THEN ''
                  WHEN dc.max IS NULL OR dc.max = '' THEN ' within ' + dc.min
                  ELSE ' within ' + dc.min + ' to ' + dc.max END) AS phrases
WITH interaction, mode, fragment, guard, phrases,
     CASE fragment WHEN 'par' THEN ', and ' ELSE ', then ' END AS sep
WITH interaction, mode, fragment, guard, sep,
     reduce(s='', p IN phrases | s + sep + p) AS joined
RETURN interaction, mode, fragment,
       'In ' + mode + ' mode, when [' + guard + '], the system shall ' +
       CASE fragment
         WHEN 'loop'  THEN 'repeatedly '
         WHEN 'break' THEN 'abort and '
         WHEN 'par'   THEN 'concurrently '
         ELSE '' END +
       substring(joined, size(sep)) + '.' AS requirement
ORDER BY interaction, mode, fragment;
