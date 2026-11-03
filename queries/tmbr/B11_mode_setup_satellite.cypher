// B.11 Mode setup for the satellite example: the file-transfer loop (and the alt
// acknowledgement and break timeout it contains) realise a single Update mode.
MERGE (mUpd:STATE {id:'mode_update'}) SET mUpd.name = 'Update'
WITH mUpd
MATCH (loop:SD:HYPERNODE {operator:'loop'})
MERGE (loop)-[:IS_PART_OF]->(mUpd);
