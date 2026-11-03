// B.2 Schema view: the lifeline-event-message-fragment structure of each diagram.
// The relationships are named (c, p1, ...) so that the Neo4j Browser draws them.
MATCH (ll:LIFELINE)-[c:COVERS]->(e:EVENT)
OPTIONAL MATCH (e)-[p1:IS_PART_OF]->(msg:MESSAGE)
OPTIONAL MATCH (e)-[p2:IS_PART_OF]->(op:SD:HYPERNODE:OPERAND)-[p3:IS_PART_OF]->(h:SD:HYPERNODE)
OPTIONAL MATCH (msg)-[cf:CONTROL_FLOW]->(msg2:MESSAGE)
RETURN *;
