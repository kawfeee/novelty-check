-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create proposals table
CREATE TABLE IF NOT EXISTS proposals (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    full_text TEXT NOT NULL,
    embedding VECTOR(768) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for vector similarity search using cosine distance
CREATE INDEX IF NOT EXISTS proposals_embedding_idx 
ON proposals 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Create index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS proposals_created_at_idx 
ON proposals (created_at DESC);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_proposals_updated_at 
BEFORE UPDATE ON proposals
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
