-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for agents_hub
CREATE SCHEMA IF NOT EXISTS agents_hub;

-- Create collection table for RAG
CREATE TABLE IF NOT EXISTS pg_collection ( 
    name varchar NULL,
    cmetadata json NULL,
    uuid uuid NOT NULL,
    CONSTRAINT langchain_pg_collection_pkey PRIMARY KEY (uuid)
);

-- Create embedding table for RAG
CREATE TABLE IF NOT EXISTS pg_embedding ( 
    collection_id uuid NULL,
    embedding vector NULL,
    "document" varchar NULL,
    cmetadata json NULL,
    custom_id varchar NULL,
    "uuid" uuid NOT NULL,
    CONSTRAINT pg_embedding_pkey PRIMARY KEY (uuid),
    CONSTRAINT pg_embedding_collection_id_fkey FOREIGN KEY (collection_id) REFERENCES pg_collection("uuid") ON DELETE CASCADE
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS pg_embedding_collection_id_idx ON pg_embedding USING btree (collection_id);

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
