// B.10 Mode setup for the Smartlight example: link combined fragments to the
// operational-mode states they realise. Run as a single statement so that the
// mode variables remain in scope for the MERGE links.
MERGE (mCtl:STATE {id:'mode_control'}) SET mCtl.name = 'Control'
MERGE (mMon:STATE {id:'mode_status'})  SET mMon.name = 'Status Check'
WITH mCtl, mMon
MATCH (alt:SD:HYPERNODE  {operator:'alt'})
MATCH (loop:SD:HYPERNODE {operator:'loop'})
MERGE (alt)-[:IS_PART_OF]->(mCtl)
MERGE (loop)-[:IS_PART_OF]->(mMon);
