# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import os

import cohere
import faiss
import numpy as np


class Client:
    """This class wraps around a Cohere client to facilitate semantic search using query embeddings."""

    def __init__(self, input_embeddings: str) -> None:
        """Initialize the client using embeddings of documents (blocks) provided as input_embeddings."""
        self._co = cohere.Client(os.environ["COHERE_TOKEN"])
        self._embeddings = np.load(input_embeddings)
        self._index = faiss.IndexFlatIP(self._embeddings['embeddings'].shape[-1])  # inner product index
        f32_embeddings = self._embeddings['embeddings'].astype(np.float32)  # faiss only supports f32

        # normalise embeddings, so that the inner product is the cosine similarity
        normal_f32_embeddings = f32_embeddings / \
            np.linalg.norm(f32_embeddings, ord=2, axis=-1, keepdims=True)
        self._index.add(normal_f32_embeddings)

    def n_embeddings(self) -> int:
        """Return number of embeddings."""
        return len(self._embeddings['embeddings'])

    def search(self, query: str, n_results: int):
        """Execute a search by embedding the query and finding similar block embeddings."""
        q_embedding = self._co.embed([query], model='large').embeddings
        q = np.array(q_embedding, dtype=np.float32)

        # normalise the query too
        normal_q = q / np.linalg.norm(q, ord=2, axis=-1, keepdims=True)
        distances, index = map(np.squeeze, self._index.search(normal_q, n_results))

        results = []
        for i, dist in zip(index, distances):
            result = {"block_url": self._embeddings['block_links'][i], "doc_url": self._embeddings['doc_links'][i]}
            results.append(result)
        return results
