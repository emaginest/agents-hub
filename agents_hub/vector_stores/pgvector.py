"""
PGVector implementation for the Agents Hub framework.

This module provides a flexible interface for working with PostgreSQL's pgvector extension,
allowing users to build their own vector similarity search solutions.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import logging
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
import numpy as np
from agents_hub.tools.base import BaseTool
from agents_hub.llm.base import BaseLLM
from agents_hub.utils.document import chunk_text

# Initialize logger
logger = logging.getLogger(__name__)


class PGVector(BaseTool):
    """
    Tool for working with PostgreSQL's pgvector extension.

    This tool provides a flexible interface for vector similarity search,
    allowing users to build their own RAG solutions.
    """

    def __init__(
        self,
        llm: BaseLLM,
        host: str = "localhost",
        port: int = 5432,
        database: str = "postgres",
        user: str = "postgres",
        password: str = "postgres",
        schema: str = "public",
        embedding_dimension: int = 1536,  # Default for OpenAI embeddings
        **kwargs,
    ):
        """
        Initialize the PGVector tool.

        Args:
            llm: LLM provider for generating embeddings
            host: PostgreSQL host
            port: PostgreSQL port
            database: PostgreSQL database name
            user: PostgreSQL username
            password: PostgreSQL password
            schema: PostgreSQL schema
            embedding_dimension: Dimension of embeddings
            **kwargs: Additional parameters for psycopg2.connect
        """
        super().__init__(
            name="pgvector",
            description="Work with vector embeddings in PostgreSQL for similarity search",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "create_collection",
                            "list_collections",
                            "delete_collection",
                            "add_document",
                            "add_documents",
                            "search",
                            "delete_document",
                            "get_document",
                            "count_documents",
                        ],
                        "description": "Operation to perform",
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to use",
                    },
                    "document": {
                        "type": "string",
                        "description": "Document text to add (for add_document operation)",
                    },
                    "documents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of document texts to add (for add_documents operation)",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadata to associate with the document",
                    },
                    "query": {
                        "type": "string",
                        "description": "Query text for similarity search (for search operation)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (for search operation)",
                        "default": 5,
                    },
                    "document_id": {
                        "type": "string",
                        "description": "ID of the document to retrieve or delete",
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Size of chunks when processing documents",
                        "default": 1000,
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks when processing documents",
                        "default": 200,
                    },
                    "chunk_method": {
                        "type": "string",
                        "enum": ["token", "character", "sentence"],
                        "description": "Method to use for chunking documents",
                        "default": "sentence",
                    },
                },
                "required": ["operation"],
            },
        )

        self.llm = llm

        # Ensure we're using the provided connection parameters
        # and not any potentially hardcoded values
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            **kwargs,
        }

        # Log connection parameters for debugging (without password)
        debug_params = self.connection_params.copy()
        if "password" in debug_params:
            debug_params["password"] = "*****"
        logger.info(f"PGVector initialized with connection parameters: {debug_params}")

        self.schema = schema
        self.embedding_dimension = embedding_dimension

        # Initialize the database
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the database schema."""
        try:
            # Log connection attempt
            debug_params = self.connection_params.copy()
            if "password" in debug_params:
                debug_params["password"] = "*****"
            logger.info(
                f"Attempting to connect to PostgreSQL with parameters: {debug_params}"
            )

            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    # Register UUID type
                    register_uuid()

                    # Check if pgvector extension is installed
                    cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                    if not cur.fetchone():
                        logger.info(
                            "pgvector extension not found, attempting to create it"
                        )
                        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                    else:
                        logger.info("pgvector extension is already installed")

                    # Create collection table if it doesn't exist
                    cur.execute(
                        f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.pg_collection (
                        uuid UUID PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        metadata JSONB NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                    )

                    # Create embedding table if it doesn't exist
                    cur.execute(
                        f"""
                    CREATE TABLE IF NOT EXISTS {self.schema}.pg_embedding (
                        uuid UUID PRIMARY KEY,
                        collection_id UUID NOT NULL REFERENCES {self.schema}.pg_collection(uuid) ON DELETE CASCADE,
                        embedding vector({self.embedding_dimension}),
                        document TEXT NOT NULL,
                        metadata JSONB NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        custom_id VARCHAR NULL
                    )
                    """
                    )

                    # Create index on collection name
                    cur.execute(
                        f"""
                    CREATE INDEX IF NOT EXISTS idx_pg_collection_name
                    ON {self.schema}.pg_collection(name)
                    """
                    )

                    # Create index on embedding vectors
                    cur.execute(
                        f"""
                    CREATE INDEX IF NOT EXISTS idx_pg_embedding_vector
                    ON {self.schema}.pg_embedding
                    USING ivfflat (embedding vector_l2_ops)
                    """
                    )

                    conn.commit()

                    logger.info("PGVector database initialized successfully")

        except psycopg2.OperationalError as e:
            # Handle connection errors specifically
            logger.error(f"PostgreSQL connection error: {e}")
            logger.error(
                "Please check your connection parameters and ensure the database is running."
            )
            logger.error(
                "If using environment variables, make sure they are set correctly."
            )
            raise
        except Exception as e:
            logger.exception(f"Error initializing PGVector database: {e}")
            raise

    async def run(
        self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Perform PGVector operations.

        Args:
            parameters: Parameters for the tool
            context: Optional context information

        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")

        try:
            if operation == "create_collection":
                return await self._create_collection(parameters)

            elif operation == "list_collections":
                return await self._list_collections()

            elif operation == "delete_collection":
                return await self._delete_collection(parameters)

            elif operation == "add_document":
                return await self._add_document(parameters)

            elif operation == "add_documents":
                return await self._add_documents(parameters)

            elif operation == "search":
                return await self._search(parameters)

            elif operation == "delete_document":
                return await self._delete_document(parameters)

            elif operation == "get_document":
                return await self._get_document(parameters)

            elif operation == "count_documents":
                return await self._count_documents(parameters)

            else:
                return {"error": f"Unknown operation: {operation}"}

        except Exception as e:
            logger.exception(f"Error in PGVector tool: {e}")
            return {"error": str(e)}

    async def _create_collection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new collection.

        Args:
            parameters: Operation parameters

        Returns:
            Creation result
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {
                "error": "collection_name parameter is required for create_collection operation"
            }

        metadata = parameters.get("metadata", {})

        try:
            # Check if collection already exists
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        f"SELECT uuid FROM {self.schema}.pg_collection WHERE name = %s",
                        (collection_name,),
                    )
                    existing = cur.fetchone()

                    if existing:
                        return {
                            "collection_id": str(existing["uuid"]),
                            "collection_name": collection_name,
                            "already_exists": True,
                        }

                    # Create new collection
                    collection_id = uuid.uuid4()
                    cur.execute(
                        f"""
                        INSERT INTO {self.schema}.pg_collection (uuid, name, metadata)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            collection_id,
                            collection_name,
                            json.dumps(metadata) if metadata else None,
                        ),
                    )

                    conn.commit()

                    return {
                        "collection_id": str(collection_id),
                        "collection_name": collection_name,
                        "created": True,
                    }

        except Exception as e:
            logger.exception(f"Error creating collection: {e}")
            return {"error": f"Failed to create collection: {str(e)}"}

    async def _list_collections(self) -> Dict[str, Any]:
        """
        List all collections.

        Returns:
            List of collections
        """
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        f"""
                        SELECT uuid, name, metadata, created_at
                        FROM {self.schema}.pg_collection
                        ORDER BY name
                        """
                    )

                    collections = []
                    for row in cur.fetchall():
                        collections.append(
                            {
                                "collection_id": str(row["uuid"]),
                                "collection_name": row["name"],
                                "metadata": row["metadata"],
                                "created_at": (
                                    row["created_at"].isoformat()
                                    if row["created_at"]
                                    else None
                                ),
                            }
                        )

                    return {
                        "collections": collections,
                        "count": len(collections),
                    }

        except Exception as e:
            logger.exception(f"Error listing collections: {e}")
            return {"error": f"Failed to list collections: {str(e)}"}

    async def _delete_collection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a collection.

        Args:
            parameters: Operation parameters

        Returns:
            Deletion result
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {
                "error": "collection_name parameter is required for delete_collection operation"
            }

        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    # Get collection ID
                    cur.execute(
                        f"SELECT uuid FROM {self.schema}.pg_collection WHERE name = %s",
                        (collection_name,),
                    )

                    collection = cur.fetchone()
                    if not collection:
                        return {
                            "collection_name": collection_name,
                            "deleted": False,
                            "error": "Collection not found",
                        }

                    collection_id = collection[0]

                    # Delete collection (cascade will delete embeddings)
                    cur.execute(
                        f"DELETE FROM {self.schema}.pg_collection WHERE uuid = %s",
                        (collection_id,),
                    )

                    conn.commit()

                    return {
                        "collection_name": collection_name,
                        "deleted": True,
                    }

        except Exception as e:
            logger.exception(f"Error deleting collection: {e}")
            return {"error": f"Failed to delete collection: {str(e)}"}

    async def _get_collection_id(self, collection_name: str) -> Optional[uuid.UUID]:
        """
        Get the ID of a collection by name.

        Args:
            collection_name: Name of the collection

        Returns:
            Collection ID or None if not found
        """
        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT uuid FROM {self.schema}.pg_collection WHERE name = %s",
                        (collection_name,),
                    )

                    result = cur.fetchone()
                    return result[0] if result else None

        except Exception as e:
            logger.exception(f"Error getting collection ID: {e}")
            return None

    async def _add_document(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a document to a collection.

        Args:
            parameters: Operation parameters

        Returns:
            Addition result
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {
                "error": "collection_name parameter is required for add_document operation"
            }

        document = parameters.get("document")
        if not document:
            return {
                "error": "document parameter is required for add_document operation"
            }

        metadata = parameters.get("metadata", {})
        chunk_size = parameters.get("chunk_size", 1000)
        chunk_overlap = parameters.get("chunk_overlap", 200)
        chunk_method = parameters.get("chunk_method", "sentence")

        try:
            # Get collection ID
            collection_id = await self._get_collection_id(collection_name)
            if not collection_id:
                # Create collection if it doesn't exist
                create_result = await self._create_collection(
                    {"collection_name": collection_name}
                )
                if "error" in create_result:
                    return create_result

                collection_id = uuid.UUID(create_result["collection_id"])

            # Process document
            if len(document) > chunk_size:
                # Chunk the document
                chunks = chunk_text(
                    text=document,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    chunk_method=chunk_method,
                )

                # Add each chunk
                document_ids = []
                for i, chunk in enumerate(chunks):
                    # Add chunk metadata
                    chunk_metadata = metadata.copy() if metadata else {}
                    chunk_metadata.update(
                        {
                            "chunk_index": i,
                            "chunk_count": len(chunks),
                        }
                    )

                    # Generate embedding
                    embedding = await self.llm.get_embedding(chunk)

                    # Add to database
                    document_id = str(uuid.uuid4())

                    with psycopg2.connect(**self.connection_params) as conn:
                        with conn.cursor() as cur:
                            # Convert embedding to PostgreSQL vector format
                            embedding_str = f"[{','.join(map(str, embedding))}]"

                            cur.execute(
                                f"""
                                INSERT INTO {self.schema}.pg_embedding
                                (uuid, collection_id, embedding, document, metadata)
                                VALUES (%s, %s, %s::vector, %s, %s)
                                """,
                                (
                                    document_id,
                                    collection_id,
                                    embedding_str,
                                    chunk,
                                    (
                                        json.dumps(chunk_metadata)
                                        if chunk_metadata
                                        else None
                                    ),
                                ),
                            )

                            conn.commit()

                    document_ids.append(document_id)

                return {
                    "document_ids": document_ids,
                    "collection_name": collection_name,
                    "chunk_count": len(chunks),
                }

            else:
                # Generate embedding for single document
                embedding = await self.llm.get_embedding(document)

                # Add to database
                document_id = str(uuid.uuid4())

                with psycopg2.connect(**self.connection_params) as conn:
                    with conn.cursor() as cur:
                        # Convert embedding to PostgreSQL vector format
                        embedding_str = f"[{','.join(map(str, embedding))}]"

                        cur.execute(
                            f"""
                            INSERT INTO {self.schema}.pg_embedding
                            (uuid, collection_id, embedding, document, metadata)
                            VALUES (%s, %s, %s::vector, %s, %s)
                            """,
                            (
                                document_id,
                                collection_id,
                                embedding_str,
                                document,
                                json.dumps(metadata) if metadata else None,
                            ),
                        )

                        conn.commit()

                return {
                    "document_id": document_id,
                    "collection_name": collection_name,
                }

        except Exception as e:
            logger.exception(f"Error adding document: {e}")
            return {"error": f"Failed to add document: {str(e)}"}

    async def _add_documents(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add multiple documents to a collection.

        Args:
            parameters: Operation parameters

        Returns:
            Addition result
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {
                "error": "collection_name parameter is required for add_documents operation"
            }

        documents = parameters.get("documents")
        if not documents or not isinstance(documents, list):
            return {
                "error": "documents parameter (list) is required for add_documents operation"
            }

        metadata = parameters.get("metadata", {})
        chunk_size = parameters.get("chunk_size", 1000)
        chunk_overlap = parameters.get("chunk_overlap", 200)
        chunk_method = parameters.get("chunk_method", "sentence")

        try:
            results = []
            for document in documents:
                # Add each document
                result = await self._add_document(
                    {
                        "collection_name": collection_name,
                        "document": document,
                        "metadata": metadata,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "chunk_method": chunk_method,
                    }
                )

                results.append(result)

            return {
                "results": results,
                "collection_name": collection_name,
                "document_count": len(documents),
                "success_count": sum(1 for r in results if "error" not in r),
                "error_count": sum(1 for r in results if "error" in r),
            }

        except Exception as e:
            logger.exception(f"Error adding documents: {e}")
            return {"error": f"Failed to add documents: {str(e)}"}

    async def _search(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for similar documents.

        Args:
            parameters: Operation parameters

        Returns:
            Search results
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {
                "error": "collection_name parameter is required for search operation"
            }

        query = parameters.get("query")
        if not query:
            return {"error": "query parameter is required for search operation"}

        limit = parameters.get("limit", 5)

        try:
            # Get collection ID
            collection_id = await self._get_collection_id(collection_name)
            if not collection_id:
                return {
                    "collection_name": collection_name,
                    "error": "Collection not found",
                }

            # Generate embedding for query
            embedding = await self.llm.get_embedding(query)

            # Convert embedding to PostgreSQL vector format
            embedding_str = f"[{','.join(map(str, embedding))}]"

            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        f"""
                        SELECT
                            e.uuid,
                            e.document,
                            e.metadata,
                            e.created_at,
                            1 - (e.embedding <-> %s::vector) as similarity
                        FROM {self.schema}.pg_embedding e
                        WHERE e.collection_id = %s
                        ORDER BY similarity DESC
                        LIMIT %s
                        """,
                        (embedding_str, collection_id, limit),
                    )

                    results = []
                    for row in cur.fetchall():
                        results.append(
                            {
                                "document_id": str(row["uuid"]),
                                "document": row["document"],
                                "metadata": row["metadata"],
                                "similarity": float(row["similarity"]),
                                "created_at": (
                                    row["created_at"].isoformat()
                                    if row["created_at"]
                                    else None
                                ),
                            }
                        )

                    return {
                        "results": results,
                        "collection_name": collection_name,
                        "query": query,
                        "count": len(results),
                    }

        except Exception as e:
            logger.exception(f"Error searching documents: {e}")
            return {"error": f"Failed to search documents: {str(e)}"}

    async def _delete_document(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a document.

        Args:
            parameters: Operation parameters

        Returns:
            Deletion result
        """
        document_id = parameters.get("document_id")
        if not document_id:
            return {
                "error": "document_id parameter is required for delete_document operation"
            }

        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM {self.schema}.pg_embedding WHERE uuid = %s",
                        (document_id,),
                    )

                    deleted = cur.rowcount > 0
                    conn.commit()

                    return {
                        "document_id": document_id,
                        "deleted": deleted,
                    }

        except Exception as e:
            logger.exception(f"Error deleting document: {e}")
            return {"error": f"Failed to delete document: {str(e)}"}

    async def _get_document(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a document by ID.

        Args:
            parameters: Operation parameters

        Returns:
            Document information
        """
        document_id = parameters.get("document_id")
        if not document_id:
            return {
                "error": "document_id parameter is required for get_document operation"
            }

        try:
            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        f"""
                        SELECT
                            e.uuid,
                            e.document,
                            e.metadata,
                            e.created_at,
                            c.name as collection_name
                        FROM {self.schema}.pg_embedding e
                        JOIN {self.schema}.pg_collection c ON e.collection_id = c.uuid
                        WHERE e.uuid = %s
                        """,
                        (document_id,),
                    )

                    row = cur.fetchone()
                    if not row:
                        return {
                            "document_id": document_id,
                            "error": "Document not found",
                        }

                    return {
                        "document_id": str(row["uuid"]),
                        "document": row["document"],
                        "metadata": row["metadata"],
                        "collection_name": row["collection_name"],
                        "created_at": (
                            row["created_at"].isoformat() if row["created_at"] else None
                        ),
                    }

        except Exception as e:
            logger.exception(f"Error getting document: {e}")
            return {"error": f"Failed to get document: {str(e)}"}

    async def _count_documents(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Count documents in a collection.

        Args:
            parameters: Operation parameters

        Returns:
            Document count
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {
                "error": "collection_name parameter is required for count_documents operation"
            }

        try:
            # Get collection ID
            collection_id = await self._get_collection_id(collection_name)
            if not collection_id:
                return {
                    "collection_name": collection_name,
                    "error": "Collection not found",
                }

            with psycopg2.connect(**self.connection_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {self.schema}.pg_embedding WHERE collection_id = %s",
                        (collection_id,),
                    )

                    count = cur.fetchone()[0]

                    return {
                        "collection_name": collection_name,
                        "count": count,
                    }

        except Exception as e:
            logger.exception(f"Error counting documents: {e}")
            return {"error": f"Failed to count documents: {str(e)}"}
