#!/usr/bin/python3

import argparse
import json
import requests

def valid_testcases(server, port):
    url = 'http://' + server + ':' + str(port) + '/query'
    valid_tests = [
        { "query": "limit=20", "result": '[{"date": "2012-01-01", "precipitation": 0.0, "temp_max": 12.8, "temp_min": 5.0, "wind": 4.7, "weather": "drizzle"}, {"date": "2012-01-02", "precipitation": 10.9, "temp_max": 10.6, "temp_min": 2.8, "wind": 4.5, "weather": "rain"}, {"date": "2012-01-03", "precipitation": 0.8, "temp_max": 11.7, "temp_min": 7.2, "wind": 2.3, "weather": "rain"}, {"date": "2012-01-04", "precipitation": 20.3, "temp_max": 12.2, "temp_min": 5.6, "wind": 4.7, "weather": "rain"}, {"date": "2012-01-05", "precipitation": 1.3, "temp_max": 8.9, "temp_min": 2.8, "wind": 6.1, "weather": "rain"}, {"date": "2012-01-06", "precipitation": 2.5, "temp_max": 4.4, "temp_min": 2.2, "wind": 2.2, "weather": "rain"}, {"date": "2012-01-07", "precipitation": 0.0, "temp_max": 7.2, "temp_min": 2.8, "wind": 2.3, "weather": "rain"}, {"date": "2012-01-08", "precipitation": 0.0, "temp_max": 10.0, "temp_min": 2.8, "wind": 2.0, "weather": "sun"}, {"date": "2012-01-09", "precipitation": 4.3, "temp_max": 9.4, "temp_min": 5.0, "wind": 3.4, "weather": "rain"}, {"date": "2012-01-10", "precipitation": 1.0, "temp_max": 6.1, "temp_min": 0.6, "wind": 3.4, "weather": "rain"}, {"date": "2012-01-11", "precipitation": 0.0, "temp_max": 6.1, "temp_min": -1.1, "wind": 5.1, "weather": "sun"}, {"date": "2012-01-12", "precipitation": 0.0, "temp_max": 6.1, "temp_min": -1.7, "wind": 1.9, "weather": "sun"}, {"date": "2012-01-13", "precipitation": 0.0, "temp_max": 5.0, "temp_min": -2.8, "wind": 1.3, "weather": "sun"}, {"date": "2012-01-14", "precipitation": 4.1, "temp_max": 4.4, "temp_min": 0.6, "wind": 5.3, "weather": "snow"}, {"date": "2012-01-15", "precipitation": 5.3, "temp_max": 1.1, "temp_min": -3.3, "wind": 3.2, "weather": "snow"}, {"date": "2012-01-16", "precipitation": 2.5, "temp_max": 1.7, "temp_min": -2.8, "wind": 5.0, "weather": "snow"}, {"date": "2012-01-17", "precipitation": 8.1, "temp_max": 3.3, "temp_min": 0.0, "wind": 5.6, "weather": "snow"}, {"date": "2012-01-18", "precipitation": 19.8, "temp_max": 0.0, "temp_min": -2.8, "wind": 5.0, "weather": "snow"}, {"date": "2012-01-19", "precipitation": 15.2, "temp_max": -1.1, "temp_min": -2.8, "wind": 1.6, "weather": "snow"}, {"date": "2012-01-20", "precipitation": 13.5, "temp_max": 7.2, "temp_min": -1.1, "wind": 2.3, "weather": "snow"}]' },
        { "query": "limit=5&weather=rain&wind=4.5", "result": '[{"date": "2012-01-02", "precipitation": 10.9, "temp_max": 10.6, "temp_min": 2.8, "wind": 4.5, "weather": "rain"}, {"date": "2012-01-29", "precipitation": 27.7, "temp_max": 9.4, "temp_min": 3.9, "wind": 4.5, "weather": "rain"}, {"date": "2012-12-11", "precipitation": 3.0, "temp_max": 7.8, "temp_min": 5.6, "wind": 4.5, "weather": "rain"}, {"date": "2013-01-26", "precipitation": 2.3, "temp_max": 8.3, "temp_min": 3.9, "wind": 4.5, "weather": "rain"}, {"date": "2013-01-27", "precipitation": 1.8, "temp_max": 5.6, "temp_min": 3.9, "wind": 4.5, "weather": "rain"}]' }
    ]
    for t in valid_tests:
        query_url = url + '?' + t["query"]
        r = requests.get(query_url)
        if r.status_code != 200:
            print('query retrieval vailed, code: ', r.status_code)
            return False
        if json.dumps(r.json()) != t["result"]:
            print('query results dont match')
            return False
    return True

def invalid_testcases(server, port):
    url = 'http://' + server + ':' + str(port)
    # try a 404
    r = requests.get(url + '/foo')
    if r.status_code == 200:
        print('invalid query succeeded')
        return False
    # try a query that uses an invalid search index
    r = requests.get(url + '/query?xlimits=100')
    if r.status_code != 400:
        print('attempted false query returned unexpected result code')
        return False
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="run http server to allow querying", default="localhost", type=str)
    parser.add_argument("--port", help="port for http server to listen to", default=8080, type=int)
    args = parser.parse_args()

    result = valid_testcases(args.server, args.port)
    if result:
        print('valid tests passed')
    else:
        print('valid tests failed')
    result = invalid_testcases(args.server, args.port)
    if result:
        print('invalid tests passed')
    else:
        print('invalid tests failed')

if __name__ == "__main__":
    main()