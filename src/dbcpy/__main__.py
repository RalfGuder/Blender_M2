#!/usr/bin/env python3
from dbcpy.dbc_file import DBCFile
from dbcpy.records.item_record import ItemRecord

def change_display_ids(item_record):
    # entry: new_display_id
    new_display_ids = {
        1501: 37388,
        15534: 27083,
    }
    try:
        item_record.display_id = new_display_ids[item_record.entry]
        return item_record
    except KeyError:
        return item_record

if __name__ == '__main__':
    with open('Item.dbc', 'r+b') as f:
        dbc_file = DBCFile.from_file(f, ItemRecord)
        some_item = dbc_file.records.find(873)
        some_item.entry = 56807
        some_item.display_id = 20300
        with open('Item.dbc.new', 'w+b') as ff:
            dbc_file.write_to_file(change_display_ids, ff)

    with open('Item.dbc.new', 'r+b') as f:
        dbc_file = DBCFile.from_file(f, ItemRecord)
        print(dbc_file.records.find(1501).display_id)
        print(dbc_file.records.find(15534).display_id)

