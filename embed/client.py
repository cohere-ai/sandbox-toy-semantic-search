# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import dataclasses
import time
from typing import List

import cohere
import numpy as np
import requests

COHERE_BATCH_SIZE = 50
COHERE_N_RETRIES = 5


@dataclasses.dataclass
class Block():
    doc_title: str
    text: str
    doc_url: str
    block_url: str


class Client:
    """This class wraps around a Cohere client to facilitate embedding blocks of text."""

    def __init__(self, api_token) -> None:

        self._co = cohere.Client(api_token)
        self._embeddings = []
        self._embed_texts = []
        self._block_links = []
        self._doc_links = []

    def embed_blocks(self, blocks: List[Block], context_window: int) -> int:
        """Given a list of blocks, embed each block using the Cohere client."""
        for block in blocks:
            embed_text = '. '.join([f"Title: {block.doc_title}", f"{block.text}"])
            self._embed_texts.append(embed_text)
            self._block_links.append(block.block_url)
            self._doc_links.append(block.doc_url)

        embs = []
        for i in range(0, len(self._embed_texts), COHERE_BATCH_SIZE):
            for _ in range(COHERE_N_RETRIES):
                try:
                    x = self._co.embed(self._embed_texts[i:i + COHERE_BATCH_SIZE], model='large',
                                       truncate='LEFT').embeddings
                    embs.extend(x)
                    break
                except requests.exceptions.ConnectionError:
                    print('Connection dropped... retrying...')
                    time.sleep(1)
                except cohere.error.CohereError:
                    # This is most likely going to happen when people get rate limited due to using a trial key.
                    # Waiting and retrying should solve the problem.
                    time.sleep(60)
            else:
                raise RuntimeError(
                    'Hit maximum number of retries connecting to the Cohere API: is there a problem with your network?')

        self._embeddings = np.array(embs)
        self._doc_links = np.array(self._doc_links)
        self._block_links = np.array(self._block_links)

        return len(self._embeddings)

    def save_embeddings(self, output_file):
        """Save embeddings as an npz file."""
        np.savez(output_file, embeddings=self._embeddings, doc_links=self._doc_links, block_links=self._block_links)
