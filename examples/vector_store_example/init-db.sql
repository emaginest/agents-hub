-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for agents_hub
CREATE SCHEMA IF NOT EXISTS public;

-- Create collection table for vector store
CREATE TABLE IF NOT EXISTS public.pg_collection (
    uuid UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    metadata JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create embedding table for vector store
CREATE TABLE IF NOT EXISTS public.pg_embedding (
    uuid UUID PRIMARY KEY,
    collection_id UUID NOT NULL REFERENCES public.pg_collection(uuid) ON DELETE CASCADE,
    embedding vector(1536),
    document TEXT NOT NULL,
    metadata JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    custom_id VARCHAR NULL
);

-- Create index on collection name
CREATE INDEX IF NOT EXISTS idx_pg_collection_name 
ON public.pg_collection(name);

-- Create index on embedding vectors
CREATE INDEX IF NOT EXISTS idx_pg_embedding_vector 
ON public.pg_embedding 
USING ivfflat (embedding vector_l2_ops);
