// B.13 TMBR table per interaction: for each mode, the fragments that realise it,
// their guards and their required messages.
MATCH (mode:STATE)<-[:IS_PART_OF]-(top:SD:HYPERNODE) WHERE top.operator IS NOT NULL
MATCH (frag:SD:HYPERNODE)-[:IS_PART_OF*0..]->(top) WHERE frag.operator IS NOT NULL
MATCH (frag)-[:IS_PART_OF]->(i:INTERACTION)
WITH DISTINCT i, mode, frag
MATCH (frag)<-[:IS_PART_OF]-(op:SD:HYPERNODE:OPERAND)<-[:IS_PART_OF]-(se:EVENT)-[:IS_PART_OF]->(msg:MESSAGE)
WHERE se.id = msg.sendEvent
RETURN i.name AS interaction, mode.name AS mode,
       frag.operator AS fragment, op.guard AS condition,
       collect(DISTINCT msg.name) AS required_messages
ORDER BY interaction, mode, fragment;
