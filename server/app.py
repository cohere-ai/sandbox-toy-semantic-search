# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import os
import logging
import pprint
from typing import List, Union

from fastapi import FastAPI, Response, status
from pydantic import BaseModel

from server.search.client import Client as SearchClient


class SearchRequest(BaseModel):
    query: str
    num_results: Union[int, None] = 5


class SearchResponse(BaseModel):
    results: List[dict]


app = FastAPI()
log = logging.getLogger("uvicorn")

client = None


def init_v2():
    global client
    log.info('fetching v2 block embeddings from local storage')
    client = SearchClient('/data/embeddings.npz', model_name=os.environ.get('COHERE_MODEL_NAME', 'large'))
    log.info(f'fetched {client.n_embeddings()} block embeddings')


@app.on_event("startup")
def init_embeddings():
    init_v2()


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    log.info(f'received search request: {request}')
    results = client.search(request.query, request.num_results)
    log.info(f'search results: {pprint.pformat(results)}')
    return SearchResponse(results=results)


@app.get("/alive")
def alive():
    return Response(status_code=status.HTTP_200_OK)


@app.get("/ready")
def ready():
    return Response(status_code=status.HTTP_200_OK)
