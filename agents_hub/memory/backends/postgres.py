"""
PostgreSQL memory backend for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from agents_hub.memory.base import BaseMemory, MemoryEntry


class PostgreSQLMemory(BaseMemory):
    """
    PostgreSQL memory backend.
    
    This class implements the BaseMemory interface using PostgreSQL.
    """
    
    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        table_prefix: str = "agents_hub_",
        **kwargs
    ):
        """
        Initialize the PostgreSQL memory backend.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            database: PostgreSQL database name
            user: PostgreSQL username
            password: PostgreSQL password
            table_prefix: Prefix for table names
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
        self.table_prefix = table_prefix
        self.memory_table = f"{table_prefix}memory"
        
        # Initialize the database
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize the database schema."""
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                # Create memory table if it doesn't exist
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.memory_table} (
                    id SERIAL PRIMARY KEY,
                    conversation_id VARCHAR(255) NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                );
                """)
                
                # Create index on conversation_id for faster lookups
                cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.memory_table}_conversation_id_idx
                ON {self.memory_table} (conversation_id);
                """)
                
                # Create index on timestamp for faster sorting
                cur.execute(f"""
                CREATE INDEX IF NOT EXISTS {self.memory_table}_timestamp_idx
                ON {self.memory_table} (timestamp);
                """)
                
                conn.commit()
    
    async def add_interaction(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a new interaction to memory.
        
        Args:
            conversation_id: Identifier for the conversation
            user_message: Message from the user
            assistant_message: Response from the assistant
            metadata: Optional additional metadata
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self.memory_table}
                    (conversation_id, user_message, assistant_message, metadata)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        conversation_id,
                        user_message,
                        assistant_message,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                conn.commit()
    
    async def get_history(
        self,
        conversation_id: str,
        limit: int = 10,
        before: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from memory.
        
        Args:
            conversation_id: Identifier for the conversation
            limit: Maximum number of interactions to retrieve
            before: Only retrieve interactions before this time
            
        Returns:
            List of interactions
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if before:
                    cur.execute(
                        f"""
                        SELECT * FROM {self.memory_table}
                        WHERE conversation_id = %s AND timestamp < %s
                        ORDER BY timestamp DESC
                        LIMIT %s
                        """,
                        (conversation_id, before, limit),
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT * FROM {self.memory_table}
                        WHERE conversation_id = %s
                        ORDER BY timestamp DESC
                        LIMIT %s
                        """,
                        (conversation_id, limit),
                    )
                
                results = cur.fetchall()
                
                # Convert to list of dicts and parse metadata
                history = []
                for row in results:
                    entry = dict(row)
                    if entry["metadata"]:
                        entry["metadata"] = json.loads(entry["metadata"])
                    history.append(entry)
                
                # Reverse to get chronological order
                history.reverse()
                
                return history
    
    async def clear_history(self, conversation_id: str) -> None:
        """
        Clear conversation history from memory.
        
        Args:
            conversation_id: Identifier for the conversation
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    DELETE FROM {self.memory_table}
                    WHERE conversation_id = %s
                    """,
                    (conversation_id,),
                )
                conn.commit()
    
    async def search_memory(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search memory for relevant interactions.
        
        Args:
            query: Search query
            conversation_id: Optional conversation ID to limit search to
            limit: Maximum number of results to return
            
        Returns:
            List of relevant interactions
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if conversation_id:
                    cur.execute(
                        f"""
                        SELECT * FROM {self.memory_table}
                        WHERE conversation_id = %s AND (
                            user_message ILIKE %s OR
                            assistant_message ILIKE %s
                        )
                        ORDER BY timestamp DESC
                        LIMIT %s
                        """,
                        (conversation_id, f"%{query}%", f"%{query}%", limit),
                    )
                else:
                    cur.execute(
                        f"""
                        SELECT * FROM {self.memory_table}
                        WHERE user_message ILIKE %s OR
                              assistant_message ILIKE %s
                        ORDER BY timestamp DESC
                        LIMIT %s
                        """,
                        (f"%{query}%", f"%{query}%", limit),
                    )
                
                results = cur.fetchall()
                
                # Convert to list of dicts and parse metadata
                matches = []
                for row in results:
                    entry = dict(row)
                    if entry["metadata"]:
                        entry["metadata"] = json.loads(entry["metadata"])
                    matches.append(entry)
                
                return matches
    
    async def get_statistics(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the memory.
        
        Args:
            conversation_id: Optional conversation ID to limit statistics to
            
        Returns:
            Dictionary of statistics
        """
        with psycopg2.connect(**self.connection_params) as conn:
            with conn.cursor() as cur:
                stats = {}
                
                # Get total number of interactions
                if conversation_id:
                    cur.execute(
                        f"""
                        SELECT COUNT(*) FROM {self.memory_table}
                        WHERE conversation_id = %s
                        """,
                        (conversation_id,),
                    )
                    stats["total_interactions"] = cur.fetchone()[0]
                    
                    # Get first and last interaction timestamps
                    cur.execute(
                        f"""
                        SELECT MIN(timestamp), MAX(timestamp) FROM {self.memory_table}
                        WHERE conversation_id = %s
                        """,
                        (conversation_id,),
                    )
                    first, last = cur.fetchone()
                    stats["first_interaction"] = first
                    stats["last_interaction"] = last
                    
                    # Get average message lengths
                    cur.execute(
                        f"""
                        SELECT AVG(LENGTH(user_message)), AVG(LENGTH(assistant_message))
                        FROM {self.memory_table}
                        WHERE conversation_id = %s
                        """,
                        (conversation_id,),
                    )
                    avg_user, avg_assistant = cur.fetchone()
                    stats["avg_user_message_length"] = round(avg_user) if avg_user else 0
                    stats["avg_assistant_message_length"] = round(avg_assistant) if avg_assistant else 0
                else:
                    # Get total number of interactions
                    cur.execute(f"SELECT COUNT(*) FROM {self.memory_table}")
                    stats["total_interactions"] = cur.fetchone()[0]
                    
                    # Get number of unique conversations
                    cur.execute(f"SELECT COUNT(DISTINCT conversation_id) FROM {self.memory_table}")
                    stats["unique_conversations"] = cur.fetchone()[0]
                    
                    # Get first and last interaction timestamps
                    cur.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM {self.memory_table}")
                    first, last = cur.fetchone()
                    stats["first_interaction"] = first
                    stats["last_interaction"] = last
                    
                    # Get average message lengths
                    cur.execute(
                        f"""
                        SELECT AVG(LENGTH(user_message)), AVG(LENGTH(assistant_message))
                        FROM {self.memory_table}
                        """
                    )
                    avg_user, avg_assistant = cur.fetchone()
                    stats["avg_user_message_length"] = round(avg_user) if avg_user else 0
                    stats["avg_assistant_message_length"] = round(avg_assistant) if avg_assistant else 0
                
                return stats
