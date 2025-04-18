-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create memory table
CREATE TABLE IF NOT EXISTS agents_hub_memory (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    assistant_message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for memory table
CREATE INDEX IF NOT EXISTS agents_hub_memory_conversation_id_idx ON agents_hub_memory (conversation_id);
CREATE INDEX IF NOT EXISTS agents_hub_memory_timestamp_idx ON agents_hub_memory (timestamp);
