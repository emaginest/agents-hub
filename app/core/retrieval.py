from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import execute_values, register_uuid
from app.config import Settings
from app.utils.monitoring import monitored_client

settings = Settings()


import uuid
import json


class VectorDatabase:
    def __init__(self):
        self.connection = None
        self.connect()

    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            # Register UUID type
            register_uuid()

            self.connection = psycopg2.connect(
                host=settings.postgres_host,
                port=settings.postgres_port,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
            )
        except Exception as e:
            raise Exception(f"Error connecting to database: {str(e)}")

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI API"""
        try:
            response = await monitored_client.embeddings.create(
                model="text-embedding-3-small", input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")

    async def get_or_create_collection(self, collection_name: str) -> uuid.UUID:
        """Get collection ID by name or create if it doesn't exist"""
        try:
            with self.connection.cursor() as cur:
                # Try to get existing collection
                cur.execute(
                    """
                    SELECT uuid FROM langchain_pg_collection
                    WHERE name = %s
                    """,
                    (collection_name,),
                )
                result = cur.fetchone()

                if result:
                    return result[0]

                # Create new collection if it doesn't exist
                collection_id = uuid.uuid4()
                cur.execute(
                    """
                    INSERT INTO langchain_pg_collection (uuid, name)
                    VALUES (%s, %s)
                    """,
                    (collection_id, collection_name),
                )
                self.connection.commit()
                return collection_id
        except Exception as e:
            raise Exception(f"Error managing collection: {str(e)}")

    async def find_similar_documents(
        self, query: str, collection_name: Optional[str] = None, limit: int = 3
    ) -> List[Dict[str, any]]:
        """Find similar documents using vector similarity search"""
        try:
            query_embedding = await self.get_embedding(query)
            # Convert to PostgreSQL vector format
            embedding_str = f"[{','.join(map(str, query_embedding))}]"

            with self.connection.cursor() as cur:
                # Build query with optional collection filter
                query = """
                    SELECT e.document, e.cmetadata, embedding <=> (%s::vector) as distance
                    FROM langchain_pg_embedding e
                    LEFT JOIN langchain_pg_collection c ON e.collection_id = c.uuid
                    WHERE e.embedding IS NOT NULL
                """
                params = [embedding_str]

                if collection_name:
                    query += " AND c.name = %s"
                    params.append(collection_name)

                query += """
                    ORDER BY embedding <=> (%s::vector)
                    LIMIT %s
                """
                params.extend([embedding_str, limit])

                cur.execute(query, params)
                results = cur.fetchall()

                similar_docs = [
                    {
                        "text": doc,
                        "metadata": metadata if metadata else {},
                        "distance": float(score),
                    }
                    for doc, metadata, score in results
                ]

                return similar_docs

        except Exception as e:
            raise Exception(f"Error finding similar documents: {str(e)}")

    async def ingest_document(
        self,
        text: str,
        metadata: Optional[Dict[str, str]] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        """Ingest a document into the vector store"""
        try:
            # Get embedding for the document
            embedding = await self.get_embedding(text)
            # Convert to PostgreSQL vector format
            embedding_str = f"[{','.join(map(str, embedding))}]"

            # Get or create collection if name provided
            collection_id = None
            if collection_name:
                collection_id = await self.get_or_create_collection(collection_name)

            # Generate document ID
            doc_id = str(uuid.uuid4())

            # Insert document, embedding, and metadata into database
            with self.connection.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO langchain_pg_embedding (id, collection_id, document, embedding, cmetadata)
                    VALUES (%s, %s, %s, (%s::vector), %s)
                    """,
                    (
                        doc_id,
                        collection_id,
                        text,
                        embedding_str,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                self.connection.commit()

        except Exception as e:
            raise Exception(f"Error ingesting document: {str(e)}")

    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


# Create a global instance
vector_db = VectorDatabase()


async def retrieve_context(
    query: str, collection_name: Optional[str] = None
) -> List[Dict[str, any]]:
    """Retrieve relevant context for the given query."""
    try:
        return await vector_db.find_similar_documents(
            query, collection_name, limit=settings.max_context_documents
        )
    except Exception as e:
        raise Exception(f"Error retrieving context: {str(e)}")


async def ingest_document(
    text: str,
    metadata: Optional[Dict[str, str]] = None,
    collection_name: Optional[str] = None,
) -> None:
    """Ingest a document into the vector store."""
    try:
        await vector_db.ingest_document(text, metadata, collection_name)
    except Exception as e:
        raise Exception(f"Error ingesting document: {str(e)}")
