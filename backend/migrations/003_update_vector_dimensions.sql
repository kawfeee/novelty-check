-- Migration to update vector dimensions for MiniLM model
-- Changes embedding from VECTOR(768) to VECTOR(384)

-- Step 1: Drop the old index
DROP INDEX IF EXISTS proposals_embedding_idx;

-- Step 2: Drop the old embedding column
ALTER TABLE proposals DROP COLUMN IF EXISTS embedding;

-- Step 3: Add new embedding column with 384 dimensions
ALTER TABLE proposals 
ADD COLUMN embedding VECTOR(384);

-- Step 4: Recreate index for vector similarity search
CREATE INDEX proposals_embedding_idx 
ON proposals 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
