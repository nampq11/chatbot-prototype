import re
from typing import List, Tuple

from datasketch import MinHash, MinHashLSH
from langchain_core.documents import Document
from loguru import logger

from src.config import Config

config = Config()

def deduplicate_documents(
    documents: List[Document],
    threshold: float = 0.7,
) -> List[Document]:
    if not documents:
        return []
    
    duplicates = find_duplicates(documents, threshold)

    logger.info(
        f"{len(duplicates) / len(documents)} documents are duplicates. Removing them."
    )

    indices_to_remove = set()
    for i, j, _ in duplicates:
        if len(documents[i].page_content) >= len(documents[j].page_content):
            indices_to_remove.add(j)
        else:
            indices_to_remove.add(i)
    
    return [doc for i, doc in enumerate(documents) if i not in indices_to_remove]

def find_duplicates(
    documents: List[Document],
    threshold: float = 0.7,
    num_perm: int = int(config.RAG_CHUNK_SIZE *0.5),
) -> List[Tuple[int, int, float]]:
    minhashes = []

    for doc in documents:
        minhash = MinHash(num_perm=num_perm)
        text = doc.page_content.lower()
        words = re.findall(r"\w+", text)

        for i in range(len(words) - 3):
            shingle = " ".join(words[i : i + 3])
            minhash.update(shingle.encode("utf-8"))
        minhashes.append(minhash)

    lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)

    for i, minhash in enumerate(minhashes):
        lsh.insert(i, minhash)
    
    duplicates = []
    for i, minhash in enumerate(minhashes):
        similar_docs = lsh.query(minhash)

        similar_docs = [j for j in similar_docs if j != i]
        
        for j in similar_docs:
            similarity = minhashes[i].jaccard(minhashes[j])
            if similarity >= threshold:
                pair = tuple(sorted([i, j]))
                duplicate_info = (*pair, similarity)
                if duplicate_info not in duplicates:
                    duplicates.append(duplicate_info)
    
    return duplicates

