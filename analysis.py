#!/usr/bin/python3

import argparse
from model.logparser import *
from model.util import *

def count_spell(in_path, out_path):

    spells = set()
    with open(in_path, 'r') as fin:
        for line in fin:
            item = log_object_factory(line)
            if item.event == KEY_EVENT_SPELL_CAST_SUCCESS:
                key = f'{item.spell_id} {item.spell_name}'
                spells.add(key)
    with open(out_path, 'w') as fout:
        for k in spells:
            fout.write(k+'\n')

def count_guid(in_path, out_path):
    guids = set()
    with open(in_path, 'r') as fin:
        for line in fin:
            items = extract_guid_from_line(line)
            guids = guids | set(items)
    data = [[get_time_string_from_guid(guid), guid] for guid in guids]
    data = sorted(data, key = lambda x: x[0])

    with open(out_path, 'w') as fout:
        for line in data:
            fout.write(f'{line[0]} {line[1]}\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", type=str, choices=['count-spell','count-guid'])
    parser.add_argument('-i', type=str, help='input path')
    parser.add_argument('-o', type=str, help='output path')
    args = parser.parse_args()

    if args.cmd == 'count-spell':
        count_spell(args.i, args.o)
    if args.cmd == 'count-guid':
        count_guid(args.i, args.o)  

