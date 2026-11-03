// B.12 Mode setup for the optical-instrument example of Wach (their Figure 11):
// the mission-lifetime loop (with the par of concurrent exchanges it contains)
// realises a single Mission mode.
MERGE (mMiss:STATE {id:'mode_mission'}) SET mMiss.name = 'Mission'
WITH mMiss
MATCH (loop:SD:HYPERNODE {operator:'loop'})
MERGE (loop)-[:IS_PART_OF]->(mMiss);
