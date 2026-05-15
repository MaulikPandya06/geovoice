import os
from openai import OpenAI
from dotenv import load_dotenv
from core.models import Statement, StatementChunk
from core.services.chunking_service import chunk_text

load_dotenv()

# NVIDIA NIM client — OpenAI-compatible interface, just different base_url
def get_nvidia_client():

    nvidia_api_key = os.getenv(
        "NVIDIA_NIM_API_KEY"
    )

    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_api_key,
    )

EMBEDDING_MODEL = "nvidia/nv-embedqa-e5-v5"  # best for Q&A retrieval RAG
EMBEDDING_DIMENSIONS = 1024


def get_passage_embedding(text: str) -> list[float]:
    """
    Use this when embedding Statement chunks going INTO the database.
    input_type='passage' tells the model this is a document being stored.
    """
    nvidia_client = get_nvidia_client()
    response = nvidia_client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL,
        encoding_format="float",
        extra_body={
            "input_type": "passage",
            "truncate": "END"  # if text exceeds token limit, truncate the end
        }
    )
    return response.data[0].embedding  # list of 1024 floats


def get_query_embedding(text: str) -> list[float]:
    """
    Use this when embedding a user's QUESTION at search time.
    input_type='query' is optimized for retrieval matching.
    """
    nvidia_client = get_nvidia_client()
    response = nvidia_client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL,
        encoding_format="float",
        extra_body={
            "input_type": "query",
            "truncate": "END"
        }
    )
    return response.data[0].embedding


def embed_statement(statement: Statement) -> int:
    """
    1. Delete any existing chunks for this statement (for re-embedding support)
    2. Split statement.text into chunks
    3. Call NVIDIA API for each chunk
    4. Save each chunk with its embedding to StatementChunk

    Returns: number of chunks created
    """
    # Clean up old chunks if re-embedding
    statement.chunks.all().delete()

    chunks = chunk_text(statement.text, chunk_size=400, overlap=50)

    for index, chunk in enumerate(chunks):
        embedding_vector = get_passage_embedding(chunk)

        StatementChunk.objects.create(
            statement=statement,
            chunk_index=index,
            chunk_text=chunk,
            embedding=embedding_vector
        )
        print(
            f"✓ Statement {statement.id} | "
            f"Chunk {index + 1}/{len(chunks)}"
        )

    return len(chunks)
