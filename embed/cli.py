# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.
"""Fetch embeddings from cohere and write out to different formats."""

import os
import typing

import click
import jsonlines

from embed.client import Block, Client
from embed.localtxt.client import Client as LocalTextClient


@click.group(invoke_without_command=False)
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.option('--input-blocks', help='path to input file of jsonl-formatted blocks')
@click.option('--output-file', help='path to output file of embeddings')
@click.option('--context-window', help='number of surrounding blocks included while embedding', default=6)
@click.option('--api_token', help='Cohere API token', default=None)
@click.option('--model_name', help='Cohere Model name', default='large')
def blocks(input_blocks: str,
           output_file: str,
           context_window: int,
           api_token: typing.Optional[str] = None,
           model_name: typing.Optional[str] = 'large') -> None:
    """Embed a collection of text blocks presented in a jsonl file."""

    blocks = []

    # Retrieve all blocks from a jsonl file
    click.secho(f'fetching blocks from input file', fg='blue')
    with jsonlines.open(input_blocks) as reader:
        for obj in reader:
            blocks.append(
                Block(doc_title=obj['doc_title'], text=obj['text'], doc_url=obj['doc_url'], block_url=obj['block_url']))
    click.secho(f'fetched {len(blocks)} blocks', fg='blue')

    if api_token or "COHERE_TOKEN" in os.environ:
        api_token = api_token if api_token else os.environ["COHERE_TOKEN"]
    else:
        raise KeyError("Could not find Cohere API key in kwargs or environment.")

    client = Client(api_token, model_name=model_name)

    # Embed all blocks using the Cohere client
    click.secho(f'fetching embeddings from discovered blocks', fg='cyan')
    n_embeddings = client.embed_blocks(blocks, context_window)
    click.secho(f'fetched {n_embeddings} block embeddings', fg='cyan')

    if output_file:
        click.secho(f'writing {n_embeddings} embeddings to local storage.', fg='green')
        client.save_embeddings(output_file)
        click.secho(f'Done. Output is in {output_file}.', fg='green')


@cli.command()
@click.option('--root-dir', help='path to search recursively for text files')
@click.option('--output-file', help='path to output file of embeddings')
@click.option('--context-window', help='number of surrounding blocks included while embedding', default=6)
@click.option('--api_token', help='Cohere API token', default=None)
@click.option('--model_name', help='Cohere Model name', default='large')
def localtxt(root_dir,
             output_file,
             context_window,
             api_token: typing.Optional[str] = None,
             model_name: typing.Optional[str] = 'large'):
    """Retrieve all blocks from text documents in a root dir, and embed them."""

    text_client = LocalTextClient(root_dir)

    # Get all blocks from text files in root_dir
    click.secho("Scanning local filesystem for blocks...")
    blocks = text_client.get_blocks()
    click.secho(f"Found {len(blocks)} blocks")

    if api_token or "COHERE_TOKEN" in os.environ:
        api_token = api_token if api_token else os.environ["COHERE_TOKEN"]
    else:
        raise KeyError("Could not find Cohere API key in kwargs or environment.")

    client = Client(api_token, model_name=model_name)

    # Embed all blocks using the Cohere client
    click.secho(f'fetching embeddings from discovered blocks', fg='cyan')
    n_embeddings = client.embed_blocks(blocks, context_window)
    click.secho(f'fetched {n_embeddings} block embeddings', fg='cyan')

    if output_file:
        click.secho(f'writing {n_embeddings} embeddings to local storage.', fg='green')
        client.save_embeddings(output_file)
        click.secho(f'Done. Output is in {output_file}.', fg='green')
