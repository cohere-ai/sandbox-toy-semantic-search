# Copyright (c) 2022 Cohere Inc. and its affiliates.
#
# Licensed under the MIT License (the "License");
# you may not use this file except in compliance with the License.
#
# You may obtain a copy of the License in the LICENSE file at the top
# level of this repository.

import glob
import os
from pydoc import doc

from ..client import Block


class Client:

    def __init__(self, rootdir):
        self.rootdir = rootdir

    def get_blocks(self):
        """Get list of indexable blocks contained in all documents in the root directory."""
        globstr = os.path.join(self.rootdir, '**/*.txt')
        files = glob.glob(globstr, recursive=True)
        blocks = []
        for file in files:
            doc_url = file
            with open(file, 'r') as f:
                lines = []
                block_url = 0
                for linenum, line in enumerate(f, start=1):
                    line = line.strip()

                    if len(line) == 0:
                        # blocks seperated by blank lines, so write a new block.
                        if len(lines) == 0:
                            continue  # skip empty 'blocks'.

                        text = ' '.join(lines)
                        if len(text.strip()) == 0:
                            continue
                        text = ' '.join(lines)
                        doc_url = doc_url
                        block_url = str(block_url)  # make compatible with rest of api
                        doc_title = doc_url
                        blocks.append(Block(doc_title=doc_title, text=text, doc_url=doc_url, block_url=block_url))
                        # reset
                        lines = []
                    else:
                        lines.append(line)
                        if len(lines) == 1:
                            block_url = linenum

        return blocks
