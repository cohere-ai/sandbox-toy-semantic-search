#/usr/bin/env python

# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.
"""Execute semantic search by retrieving documents which best match a query according to its embedding."""

import argparse
import json

import requests

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('query', type=str, help='question to search')
    parser.add_argument('-n', '--num_results', type=int, default=5, help='number of results to return')
    args = parser.parse_args()

    query = {'query': args.query, 'num_results': args.num_results}
    response = requests.post('http://localhost:8080/search',
                             headers={
                                 'accept': 'application/json',
                                 'Content-Type': 'application/json'
                             },
                             data=json.dumps(query)).json()
    for result in response['results']:
        print(f"{result['doc_url']}:{result['block_url']}:0:")
