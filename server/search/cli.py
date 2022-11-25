# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.
"""semantic search against notion block embeddings using cohere"""

import json
import pprint

import click
import httpx
from search.client import Client as ClientV2


@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.option('--version', help='specify version of search algorithm and embedding file format', default=2)
@click.option('--input-embeddings', help='path to input file of embeddings')
@click.option('--num-results', default=3)
@click.option('--model_name', help='Cohere model name', default='large')
def blocks(input_embeddings: str, num_results: int, model_name: str) -> None:
    """semantic search against notion block embeddings using cohere"""
    client = None

    click.secho(f'fetching block embeddings from local storage', fg='blue')
    client = ClientV2(input_embeddings, model_name=model_name)
    click.secho(f'indexed {client.n_embeddings()} block embeddings', fg='blue')

    query = click.prompt('semantic search query')
    results = client.search(query, num_results)
    click.secho(pprint.pformat(results), fg='blue')


@cli.command()
@click.option('--version', help='specify version of search algorithm and embedding file format', default=2)
@click.option('--base-url',
              help='http base url of a backend service',
              default='https://notion-semantic-search-backend-a2dmelps2q-uc.a.run.app')
@click.option('--num-results', default=3)
def request(version: int, base_url: str, num_results: int) -> None:
    """issue a semantic search request against a search backend"""

    query = click.prompt('semantic search query')

    path = "/search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {"version": version, "query": query, "num_results": num_results}

    with httpx.Client(base_url=base_url, timeout=None) as client:
        response = client.request(method="post", url=path, headers=headers, data=json.dumps(data))
        click.secho(pprint.pformat(response.json()), fg='blue')
