-- Migration to refactor proposals table for API-only backend
-- Renames title -> application_number and full_text -> extracted_text

-- Step 1: Rename columns
ALTER TABLE proposals 
RENAME COLUMN title TO application_number;

ALTER TABLE proposals 
RENAME COLUMN full_text TO extracted_text;

-- Step 2: Add unique constraint on application_number
ALTER TABLE proposals 
ADD CONSTRAINT unique_application_number UNIQUE (application_number);

-- Step 3: Create index on application_number for faster lookups
CREATE INDEX IF NOT EXISTS idx_application_number 
ON proposals (application_number);
