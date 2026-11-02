import xml.etree.ElementTree as ET
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
xmi = "{http://www.omg.org/spec/XMI/20131001}"

# ---- change xxxx to your exported model file -----------------------
FILE_NAME = 'XXXX'
# --------------------------------------------------------------------


def local(tag):
    return tag.split('}')[-1]


def get_blocks_and_actors(root):
    block_class_ids = set()
    for el in root.iter():
        if local(el.tag) == 'Block' and el.get('base_Class'):
            block_class_ids.add(el.get('base_Class'))
    records = []
    for el in root.iter('packagedElement'):
        t = el.get(xmi + 'type'); eid = el.get(xmi + 'id'); name = el.get('name')
        if t == 'uml:Class' and eid in block_class_ids:
            records.append({'id': eid, 'name': name or '', 'kind': 'BLOCK'})
        elif t == 'uml:Actor':
            records.append({'id': eid, 'name': name or '', 'kind': 'ACTOR'})
    logging.info('Blocks/actors: %d', len(records))
    return records


def get_instances(root):
    instances = []
    for el in root.iter('ownedAttribute'):
        if el.get(xmi + 'type') == 'uml:Property' and el.get('type'):
            instances.append({'id': el.get(xmi + 'id'),
                              'name': el.get('name') or '',
                              'type': el.get('type')})
    logging.info('Instances: %d', len(instances))
    return instances


def guard_text(operand):
    guard = operand.find('guard')
    if guard is None:
        return ''
    spec = guard.find('specification')
    if spec is not None and spec.get('value'):
        return spec.get('value')
    return ''

def get_duration_constraints(inter, root):
    dur_val = {}
    for el in root.iter():
        if el.get(xmi + 'type') == 'uml:Duration':
            for c in el:
                if local(c.tag) == 'expr' and c.get('value') is not None:
                    dur_val[el.get(xmi + 'id')] = c.get('value')
    results = []
    for rule in inter.iter('ownedRule'):
        if rule.get(xmi + 'type') != 'uml:DurationConstraint':
            continue
        constrained = (rule.get('constrainedElement') or '').split()
        for c in rule:
            if local(c.tag) == 'constrainedElement':
                ref = c.get(xmi + 'idref')
                if ref:
                    constrained.append(ref)
        for spec in rule:
            if local(spec.tag) == 'specification' and spec.get(xmi + 'type') == 'uml:DurationInterval':
                min_ref = spec.get('min')
                max_ref = spec.get('max')
                results.append({
                    'id': rule.get(xmi + 'id'),
                    'min': dur_val.get(min_ref, ''),
                    'max': dur_val.get(max_ref, ''),
                    'constrainedElements': constrained,
                })
    return results


def parse_fragment(frag):
    record = {'id': frag.get(xmi + 'id'),
              'operator': frag.get('interactionOperator'),
              'covered_lifelines': [c.get(xmi + 'idref') for c in frag.findall('covered')
                                    if c.get(xmi + 'idref')],
              'operands': []}
    descendants = []
    for operand in frag.findall('operand'):
        op_rec = {'id': operand.get(xmi + 'id'),
                  'guard_condition': guard_text(operand),
                  'trapped_events': [], 'nested_fragments': []}
        for child in operand:
            ctype = child.get(xmi + 'type')
            if ctype == 'uml:MessageOccurrenceSpecification':
                op_rec['trapped_events'].append(child.get(xmi + 'id'))
            elif ctype == 'uml:CombinedFragment':
                nrec, ndesc = parse_fragment(child)
                op_rec['nested_fragments'].append(child.get(xmi + 'id'))
                descendants.append(nrec)
                descendants.extend(ndesc)
        record['operands'].append(op_rec)
    return record, descendants


def parse_interaction(inter, root):
    iid = inter.get(xmi + 'id')
    data = {'id': iid, 'name': inter.get('name') or '',
            'lifelines': [], 'events': [], 'messages': [], 'fragments': [],
            'durations': []} 

    for ll in inter.findall('lifeline'):
        covers = [c.get(xmi + 'idref') for c in ll.findall('coveredBy')
                  if c.get(xmi + 'idref')]
        data['lifelines'].append({'id': ll.get(xmi + 'id'),
                                  'name': ll.get('name') or '',
                                  'represents': ll.get('represents'),
                                  'covers': covers})

    for f in inter.iter('fragment'):
        if f.get(xmi + 'type') == 'uml:MessageOccurrenceSpecification':
            cov = f.find('covered')
            data['events'].append({'id': f.get(xmi + 'id'),
                                   'message': f.get('message'),
                                   'lifeline': cov.get(xmi + 'idref') if cov is not None else None})

    event_pos = {e['id']: i for i, e in enumerate(data['events'])}
    raw = []
    for m in inter.findall('message'):
        mid = m.get(xmi + 'id')
        if not mid:
            continue
        send = m.get('sendEvent')
        recv = m.get('receiveEvent')
        if send and recv:
            kind = 'NORMAL'
        elif send and not recv:
            kind = 'LOST'
        elif recv and not send:
            kind = 'FOUND'
        else:
            kind = 'NORMAL'  
        pos = event_pos.get(send if send else recv, 10**9)
        raw.append({'id': mid, 'name': m.get('name') or '',
                    'sendEvent': send,
                    'receiveEvent': recv,
                    'kind': kind,
                    '_pos': pos})
    raw.sort(key=lambda x: x['_pos'])
    for order, m in enumerate(raw):
        m['order'] = order
        del m['_pos']
    data['messages'] = raw

    nested_ids = set()
    for operand in inter.iter('operand'):
        for child in operand:
            if child.get(xmi + 'type') == 'uml:CombinedFragment':
                nested_ids.add(child.get(xmi + 'id'))
    seen = set()
    for frag in inter.findall('fragment'):
        if frag.get(xmi + 'type') != 'uml:CombinedFragment':
            continue
        fid = frag.get(xmi + 'id')
        if fid in nested_ids or fid in seen:
            continue
        rec, desc = parse_fragment(frag)
        data['fragments'].append(rec)
        seen.add(fid)
        for d in desc:
            if d['id'] not in seen:
                data['fragments'].append(d)
                seen.add(d['id'])

    data['durations'] = get_duration_constraints(inter, root) 
    return data


def main_function():
    try:
        root = ET.parse(FILE_NAME).getroot()
    except FileNotFoundError:
        print(f"ERROR: Could not find {FILE_NAME}. Put it in this folder.")
        return

    interactions = []
    for el in root.iter():
        if el.get(xmi + 'type') == 'uml:Interaction':
            interactions.append(parse_interaction(el, root))

    data = {'blocks': get_blocks_and_actors(root),
            'instances': get_instances(root),
            'interactions': interactions}

    with open('sequence_diagram_data.json', 'w') as fh:
        json.dump(data, fh, indent=4)

    print("SUCCESS: sequence_diagram_data.json written.")
    print(f"  {len(data['blocks'])} blocks/actors, {len(data['instances'])} instances, "
          f"{len(interactions)} interaction(s):")
    for it in interactions:
        print(f"    - {it['id'][-5:]} name={it['name']!r}: {len(it['lifelines'])} lifelines, "
              f"{len(it['events'])} events, {len(it['messages'])} messages, "
              f"{len(it['fragments'])} fragments, {len(it['durations'])} durations")


if __name__ == '__main__':
    main_function()
