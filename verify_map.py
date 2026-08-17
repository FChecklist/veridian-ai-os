import json
d = json.load(open('coverage_map.json'))
print('top-level len:', len(d))
print('items len:', len(d['items']))
print('keys:', list(d.keys()))

qm = json.load(open('queue_status_map.json'))
ok = 0
bad = 0
for it in d['items']:
    tid = it.get('matching_task_id')
    if tid is None:
        continue
    if tid in qm:
        ok += 1
    else:
        bad += 1
        print('MISSING FROM QUEUE:', tid)
print('ok:', ok, 'bad:', bad)

# also verify each real id is a literal substring present in queue_list_raw.txt
raw = open('queue_list_raw.txt').read()
missing_in_raw = 0
for it in d['items']:
    tid = it.get('matching_task_id')
    if tid and (tid + " ") not in raw and (tid + "\n") not in raw:
        missing_in_raw += 1
        print('NOT LITERALLY IN RAW LIST OUTPUT:', tid)
print('missing_in_raw:', missing_in_raw)

# check item id uniqueness / count
ids = [it['item_id'] for it in d['items']]
print('unique item ids:', len(set(ids)), 'total:', len(ids))
