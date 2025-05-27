#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oracle ATP execution file"""
###############################################################################
# Project - BroadieLLM
# Filename - invoke_intg.py
# Arguments - None
# Created By - Vivek Salgia
# Creation Date - 04/29/2025
# Reviewed By -
# Reviewed Date -
# Change logs -
# Version   Date         Type   Changed By                  Comments
# =======   ============ ====   ==============  ===============================
# 1.0       29-Apr-2025   I     Vivek Salgia    Initial Creation
###############################################################################

from phi.embedder.openai import OpenAIEmbedder
from phi.vectordb.chroma import ChromaDb
from phi.knowledge.csv import CSVKnowledgeBase
import os


def create_vectordb(filename):
    print(os.getcwd())
    db_location = os.getenv("CHROMA_DB_LOCATION")

    if os.path.exists(filename):
        print("File found!!")

    knowledge_base = CSVKnowledgeBase(
        path=filename,
        vector_db=ChromaDb(
            collection="BroadIntegrations",
            path=db_location,
            embedder=OpenAIEmbedder(model="text-embedding-3-small"),
            persistent_client=True,
        ),
    )

    knowledge_base.load()

    return knowledge_base


if __name__ == "__main__":
    knowledge_base = create_vectordb("../storage/data.csv")
