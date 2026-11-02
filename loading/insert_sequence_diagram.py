import json
from neo4j import GraphDatabase

URI  = "bolt://xx.xxx.xx.xx:xxxx"                # <-- your Connection URL
AUTH = ("Database user ID", "PASSWORD")          # <-- your user ID and password
driver = GraphDatabase.driver(URI, auth=AUTH)

OPERATOR_LABEL = {"loop":"LOOP","alt":"ALT","opt":"OPT","par":"PAR","break":"BREAK"}


def load(tx, data):
    for b in data.get("blocks", []):
        lbl = "ACTOR" if b.get("kind") == "ACTOR" else "BLOCK"
        tx.run(f"MERGE (n:{lbl} {{id:$id}}) SET n.name=$name", id=b["id"], name=b["name"])

    for i in data.get("instances", []):
        tx.run("""
            MERGE (inst:INSTANCE {id:$id}) SET inst.name=$name
            WITH inst MATCH (b {id:$type})
            MERGE (inst)-[:IS_INSTANCE_OF]->(b)
        """, id=i["id"], name=i.get("name",""), type=i["type"])

    for it in data.get("interactions", []):
        iid = it["id"]
        tx.run("MERGE (i:INTERACTION {id:$id}) SET i.name=$name", id=iid, name=it.get("name",""))

        for ll in it.get("lifelines", []):
            tx.run("""
                MERGE (l:LIFELINE {id:$id}) SET l.name=$name
                WITH l MATCH (inst:INSTANCE {id:$rep})
                MERGE (l)-[:REPRESENTS]->(inst)
                WITH l MATCH (i:INTERACTION {id:$iid})
                MERGE (l)-[:IS_PART_OF]->(i)
            """, id=ll["id"], name=ll.get("name",""), rep=ll["represents"], iid=iid)

        for e in it.get("events", []):
            tx.run("MERGE (ev:EVENT {id:$id})", id=e["id"])
        for ll in it.get("lifelines", []):
            for eid in ll.get("covers", []):
                tx.run("""
                    MATCH (l:LIFELINE {id:$lid}), (ev:EVENT {id:$eid})
                    MERGE (l)-[:COVERS]->(ev)
                """, lid=ll["id"], eid=eid)

        for m in it.get("messages", []):
            send = m.get("sendEvent")
            recv = m.get("receiveEvent")
            kind = m.get("kind", "NORMAL")
            extra = f":{kind}" if kind in ("LOST", "FOUND") else ""
            tx.run(f"""
                MERGE (msg:MESSAGE{extra} {{id:$id}})
                SET msg.name=$name, msg.sendEvent=$send, msg.receiveEvent=$recv
                WITH msg MATCH (i:INTERACTION {{id:$iid}})
                MERGE (msg)-[:IS_PART_OF]->(i)
            """, id=m["id"], name=m.get("name", ""), send=send, recv=recv, iid=iid)
            if send:
                tx.run("""
                    MATCH (msg:MESSAGE {id:$id}) MERGE (se:EVENT {id:$send})
                    MERGE (se)-[:IS_PART_OF]->(msg)
                """, id=m["id"], send=send)
            if recv:
                tx.run("""
                    MATCH (msg:MESSAGE {id:$id}) MERGE (re:EVENT {id:$recv})
                    MERGE (re)-[:IS_PART_OF]->(msg)
                """, id=m["id"], recv=recv)

        ordered = sorted(it.get("messages", []), key=lambda x: x.get("order", 0))
        for a, b in zip(ordered, ordered[1:]):
            tx.run("""
                MATCH (m1:MESSAGE {id:$a}), (m2:MESSAGE {id:$b})
                MERGE (m1)-[:CONTROL_FLOW]->(m2)
            """, a=a["id"], b=b["id"])

        frags = it.get("fragments", [])
        for f in frags:
            op = f.get("operator")
            if op is None or op not in OPERATOR_LABEL:
                raise ValueError(f"Fragment {f.get('id')} unknown operator {op!r}")
            lbl = OPERATOR_LABEL[op]
            tx.run(f"""
                MERGE (h:SD:HYPERNODE:{lbl} {{id:$id}}) SET h.operator=$op
                WITH h MATCH (i:INTERACTION {{id:$iid}})
                MERGE (h)-[:IS_PART_OF]->(i)
            """, id=f["id"], op=op, iid=iid)
        for f in frags:
            for lid in f.get("covered_lifelines", []):
                tx.run("""
                    MATCH (h:SD:HYPERNODE {id:$hid}), (l:LIFELINE {id:$lid})
                    MERGE (h)-[:COVERS]->(l)
                """, hid=f["id"], lid=lid)
            for op in f.get("operands", []):
                tx.run("""
                    MERGE (o:SD:HYPERNODE:OPERAND {id:$oid}) SET o.guard=$guard
                    WITH o MATCH (h:SD:HYPERNODE {id:$hid})
                    MERGE (o)-[:IS_PART_OF]->(h)
                """, oid=op["id"], guard=op.get("guard_condition",""), hid=f["id"])
                for eid in op.get("trapped_events", []):
                    tx.run("""
                        MATCH (o:SD:HYPERNODE:OPERAND {id:$oid})
                        MERGE (ev:EVENT {id:$eid})
                        MERGE (ev)-[:IS_PART_OF]->(o)
                    """, oid=op["id"], eid=eid)
                for nfid in op.get("nested_fragments", []):
                    tx.run("""
                        MATCH (child:SD:HYPERNODE {id:$nfid})
                        MATCH (o:SD:HYPERNODE:OPERAND {id:$oid})
                        MERGE (child)-[:IS_PART_OF]->(o)
                    """, nfid=nfid, oid=op["id"])

        for d in it.get("durations", []):
            tx.run("""
                MERGE (dc:SD:HYPERNODE:DURATION {id:$id})
                SET dc.min=$min, dc.max=$max
                WITH dc MATCH (i:INTERACTION {id:$iid})
                MERGE (dc)-[:IS_PART_OF]->(i)
            """, id=d["id"], min=d.get("min", ""), max=d.get("max", ""), iid=iid)
            for eid in d.get("constrainedElements", []):
                tx.run("""
                    MATCH (dc:SD:HYPERNODE:DURATION {id:$id})
                    MATCH (ev:EVENT {id:$eid})
                    MERGE (ev)-[:IS_PART_OF]->(dc)
                """, id=d["id"], eid=eid)
                tx.run("""
                    MATCH (dc:SD:HYPERNODE:DURATION {id:$id})
                    MATCH (m:MESSAGE {id:$eid})
                    MATCH (ev:EVENT {id: coalesce(m.sendEvent, m.receiveEvent)})
                    MERGE (ev)-[:IS_PART_OF]->(dc)
                """, id=d["id"], eid=eid)


def main():
    with open("sequence_diagram_data.json") as fh:
        data = json.load(fh)
    with driver.session() as session:
        session.execute_write(load, data)
    n = len(data.get("interactions", []))
    print(f"Loaded {n} interaction(s): messages as nodes, message-level control flow, "
          "single :IS_PART_OF containment, :INTERACTION separation, duration constraints.")


if __name__ == "__main__":
    main()
