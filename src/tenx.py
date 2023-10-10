#!/usr/bin/python3

import argparse
import csv
import json
import logging
import pathlib
import sys
from tenxserver import launch_server
from tenx_utils import sanitize_field

def load_csv(filepath):
    if not pathlib.Path(filepath).is_file():
        logging.error("{} is not a valid file or is missing", filepath)
        return None
    with open(filepath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        data = list(csv_reader)
    return data

def generate_dict_from_csv_list(data):
    # if there is no data or just 1 line (assumed to be the header line), then return
    # an empty array
    if len(data) == 0 or len(data) == 1:
        return []
    entries = []
    labels = data[0]
    for entry in data[1:]:
        if len(entry) != len(labels):
            # entry does not have the same number of fields as labels
            # so the entry will be skipped
            continue
        item = {}
        for i in range(0, len(labels)):
            # check if the value is an integer or float, and if so, convert it
            value = sanitize_field(entry[i])
            item[labels[i]] = value
        entries.append(item)
    return entries

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("datafile", help="path to csv data file")
    parser.add_argument("--server", help="run http server to allow querying", action="store_true")
    parser.add_argument("--port", help="port for http server to listen to", default=8080, type=int)
    args = parser.parse_args()

    # load the csv file and convert it to a dictionary representation
    csv_data = load_csv(args.datafile)
    if not csv_data:
        sys.exit(1)
    dict_data = generate_dict_from_csv_list(csv_data)

    # if we are not running a server, just write the data file out as json
    if not args.server:
        print(json.dumps(dict_data))
        sys.exit(0)
    else:
        launch_server(args.port, dict_data)

if __name__ == "__main__":
    main()