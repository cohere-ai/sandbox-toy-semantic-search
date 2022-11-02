#!/usr/bin/env bash

# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

if [ $# -eq 1 ]
then 
	QUERY=$1
	NUM_RESULTS=5
elif [ $# -eq 2 ]
then	
	QUERY=$1
	NUM_RESULTS=$2
else
	echo "Usage: ./ask.sh QUERY (NUM_RESULTS)"
	echo "Make sure a query containing spaces is surrounded by quotes!"
        exit 0
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

vim -u "${SCRIPT_DIR}/mappings.vimrc" +cw -M -q <(python utils/query_server.py "$QUERY" --num_results $NUM_RESULTS) 
