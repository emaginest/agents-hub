"""
PostgreSQL vector storage backend for RAG in the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor, register_uuid
from agents_hub.llm.base import BaseLLM


class PostgreSQLVectorStorage:
    """
    PostgreSQL vector storage for RAG.
    
    This class implements vector storage using PostgreSQL with pgvector.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        llm: BaseLLM,
        **kwargs
    ):
        """
        Initialize the PostgreSQL vector storage.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: PostgreSQL database name
            user: PostgreSQL username
            password: PostgreSQL password
            llm: LLM provider for generating embeddings
            **kwargs: Additional parameters for psycopg2.connect
        """
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            **kwargs
        }
        self.llm = llm
        
        # Initialize the database
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the database schema."""
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                # Register UUID type
                register_uuid()
                
                # Check if pgvector extension is installed
                cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
                if not cur.fetchone():
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                
                # Create collection table if it doesn't exist
                cur.execute("""
                CREATE TABLE IF NOT EXISTS pg_collection (
                    uuid UUID PRIMARY KEY,
                    name VARCHAR NULL,
                    cmetadata JSONB NULL
                )
                """)
                
                # Create embedding table if it doesn't exist
                cur.execute("""
                CREATE TABLE IF NOT EXISTS pg_embedding (
                    uuid UUID PRIMARY KEY,
                    collection_id UUID NULL REFERENCES pg_collection(uuid) ON DELETE CASCADE,
                    embedding VECTOR NULL,
                    document TEXT NULL,
                    cmetadata JSONB NULL,
                    custom_id VARCHAR NULL
                )
                """)
                
                # Create index on collection_id for faster lookups
                cur.execute("""
                CREATE INDEX IF NOT EXISTS pg_embedding_collection_id_idx
                ON pg_embedding (collection_id)
                """)
                
                conn.commit()
    
    async def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new collection.
        
        Args:
            name: Name of the collection
            metadata: Optional metadata for the collection
            
        Returns:
            Collection ID
        """
        collection_id = str(uuid.uuid4())
        
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pg_collection (uuid, name, cmetadata)
                    VALUES (%s, %s, %s)
                    """,
                    (
                        collection_id,
                        name,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                conn.commit()
        
        return collection_id
    
    async def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Get a collection by name, or create it if it doesn't exist.
        
        Args:
            name: Name of the collection
            metadata: Optional metadata for the collection if created
            
        Returns:
            Collection ID
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT uuid FROM pg_collection
                    WHERE name = %s
                    """,
                    (name,),
                )
                result = cur.fetchone()
                
                if result:
                    return str(result[0])
                
                # Collection doesn't exist, create it
                return await self.create_collection(name, metadata)
    
    async def add_document(
        self,
        document: str,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        custom_id: Optional[str] = None,
    ) -> str:
        """
        Add a document to a collection.
        
        Args:
            document: Document text
            collection_name: Name of the collection
            metadata: Optional metadata for the document
            custom_id: Optional custom ID for the document
            
        Returns:
            Document ID
        """
        # Get or create the collection
        collection_id = await self.get_or_create_collection(collection_name)
        
        # Generate embedding for the document
        embedding = await self.llm.get_embedding(document)
        
        # Generate a UUID for the document
        document_id = str(uuid.uuid4())
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = f"[{','.join(map(str, embedding))}]"
        
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO pg_embedding (uuid, collection_id, embedding, document, cmetadata, custom_id)
                    VALUES (%s, %s, %s::vector, %s, %s, %s)
                    """,
                    (
                        document_id,
                        collection_id,
                        embedding_str,
                        document,
                        json.dumps(metadata) if metadata else None,
                        custom_id,
                    ),
                )
                conn.commit()
        
        return document_id
    
    async def search(
        self,
        query: str,
        collection_name: Optional[str] = None,
        limit: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query
            collection_name: Optional name of the collection to search in
            limit: Maximum number of results to return
            metadata_filter: Optional filter for document metadata
            
        Returns:
            List of matching documents with similarity scores
        """
        # Generate embedding for the query
        query_embedding = await self.llm.get_embedding(query)
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if collection_name:
                    # Get the collection ID
                    cur.execute(
                        """
                        SELECT uuid FROM pg_collection
                        WHERE name = %s
                        """,
                        (collection_name,),
                    )
                    collection_result = cur.fetchone()
                    
                    if not collection_result:
                        # Collection doesn't exist
                        return []
                    
                    collection_id = collection_result["uuid"]
                    
                    # Search within the collection
                    if metadata_filter:
                        # Convert metadata filter to JSON query
                        metadata_conditions = []
                        metadata_values = []
                        
                        for key, value in metadata_filter.items():
                            metadata_conditions.append(f"cmetadata->>{len(metadata_values) + 1} = %s")
                            metadata_values.append(key)
                            metadata_conditions.append(f"cmetadata->>%s = %s")
                            metadata_values.append(key)
                            metadata_values.append(str(value))
                        
                        metadata_query = " AND ".join(metadata_conditions)
                        
                        cur.execute(
                            f"""
                            SELECT e.uuid, e.document, e.cmetadata, e.custom_id,
                                   1 - (e.embedding <=> %s::vector) AS similarity
                            FROM pg_embedding e
                            WHERE e.collection_id = %s
                              AND {metadata_query}
                            ORDER BY similarity DESC
                            LIMIT %s
                            """,
                            [embedding_str, collection_id] + metadata_values + [limit],
                        )
                    else:
                        cur.execute(
                            """
                            SELECT e.uuid, e.document, e.cmetadata, e.custom_id,
                                   1 - (e.embedding <=> %s::vector) AS similarity
                            FROM pg_embedding e
                            WHERE e.collection_id = %s
                            ORDER BY similarity DESC
                            LIMIT %s
                            """,
                            (embedding_str, collection_id, limit),
                        )
                else:
                    # Search across all collections
                    if metadata_filter:
                        # Convert metadata filter to JSON query
                        metadata_conditions = []
                        metadata_values = []
                        
                        for key, value in metadata_filter.items():
                            metadata_conditions.append(f"e.cmetadata->>{len(metadata_values) + 1} = %s")
                            metadata_values.append(key)
                            metadata_conditions.append(f"e.cmetadata->>%s = %s")
                            metadata_values.append(key)
                            metadata_values.append(str(value))
                        
                        metadata_query = " AND ".join(metadata_conditions)
                        
                        cur.execute(
                            f"""
                            SELECT e.uuid, e.document, e.cmetadata, e.custom_id,
                                   c.name AS collection_name,
                                   1 - (e.embedding <=> %s::vector) AS similarity
                            FROM pg_embedding e
                            JOIN pg_collection c ON e.collection_id = c.uuid
                            WHERE {metadata_query}
                            ORDER BY similarity DESC
                            LIMIT %s
                            """,
                            [embedding_str] + metadata_values + [limit],
                        )
                    else:
                        cur.execute(
                            """
                            SELECT e.uuid, e.document, e.cmetadata, e.custom_id,
                                   c.name AS collection_name,
                                   1 - (e.embedding <=> %s::vector) AS similarity
                            FROM pg_embedding e
                            JOIN pg_collection c ON e.collection_id = c.uuid
                            ORDER BY similarity DESC
                            LIMIT %s
                            """,
                            (embedding_str, limit),
                        )
                
                results = cur.fetchall()
                
                # Convert to list of dicts and parse metadata
                documents = []
                for row in dict(results):
                    doc = dict(row)
                    if doc["cmetadata"]:
                        doc["metadata"] = json.loads(doc["cmetadata"])
                        del doc["cmetadata"]
                    else:
                        doc["metadata"] = {}
                    
                    documents.append(doc)
                
                return documents
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if the document was deleted, False otherwise
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM pg_embedding
                    WHERE uuid = %s
                    """,
                    (document_id,),
                )
                deleted = cur.rowcount > 0
                conn.commit()
        
        return deleted
    
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection by name.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if the collection was deleted, False otherwise
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM pg_collection
                    WHERE name = %s
                    """,
                    (collection_name,),
                )
                deleted = cur.rowcount > 0
                conn.commit()
        
        return deleted
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections.
        
        Returns:
            List of collections with their metadata
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT uuid, name, cmetadata
                    FROM pg_collection
                    ORDER BY name
                    """
                )
                results = cur.fetchall()
                
                # Convert to list of dicts and parse metadata
                collections = []
                for row in results:
                    collection = dict(row)
                    if collection["cmetadata"]:
                        collection["metadata"] = json.loads(collection["cmetadata"])
                        del collection["cmetadata"]
                    else:
                        collection["metadata"] = {}
                    
                    collections.append(collection)
                
                return collections
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary of statistics
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                # Get the collection ID
                cur.execute(
                    """
                    SELECT uuid FROM pg_collection
                    WHERE name = %s
                    """,
                    (collection_name,),
                )
                collection_result = cur.fetchone()
                
                if not collection_result:
                    # Collection doesn't exist
                    return {"error": f"Collection '{collection_name}' not found"}
                
                collection_id = collection_result[0]
                
                # Get document count
                cur.execute(
                    """
                    SELECT COUNT(*) FROM pg_embedding
                    WHERE collection_id = %s
                    """,
                    (collection_id,),
                )
                document_count = cur.fetchone()[0]
                
                # Get average document length
                cur.execute(
                    """
                    SELECT AVG(LENGTH(document)) FROM pg_embedding
                    WHERE collection_id = %s
                    """,
                    (collection_id,),
                )
                avg_document_length = cur.fetchone()[0]
                
                return {
                    "collection_name": collection_name,
                    "collection_id": str(collection_id),
                    "document_count": document_count,
                    "avg_document_length": round(avg_document_length) if avg_document_length else 0,
                }
