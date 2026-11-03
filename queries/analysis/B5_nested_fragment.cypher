// B.5 Nested-fragment analysis: a combined fragment nested inside another through its operand.
MATCH (child:SD:HYPERNODE)-[:IS_PART_OF]->(:SD:HYPERNODE:OPERAND)-[:IS_PART_OF]->(parent:SD:HYPERNODE)
WHERE child.operator IS NOT NULL AND parent.operator IS NOT NULL
MATCH (child)-[:IS_PART_OF]->(i:INTERACTION)
RETURN i.name AS interaction,
       child.operator  AS nested_fragment,
       parent.operator AS inside_fragment
ORDER BY interaction;
