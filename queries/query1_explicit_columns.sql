-- Task 1: Refactor Query 1 - SELECT * to Explicit Columns
-- Description: Replaces inefficient 'SELECT *' with explicitly enumerated columns from transactions and customers tables.
-- Performance Gain: Reduces I/O overhead, network payload, and memory consumption.

SELECT 
    -- From transactions table
    t.transaction_id,    -- Unique transaction key; answers: Which transaction occurred?
    t.transaction_date,  -- Timestamp of transaction; answers: When did the sale happen?
    t.amount,            -- Financial value; answers: How much revenue was generated?
    t.customer_id,       -- Foreign key linkage; answers: Which customer initiated the transaction?
    
    -- From customers table
    c.customer_name,     -- Customer identifier name; answers: Who bought the product?
    c.country,           -- Geographic location; answers: Where is the customer located?
    c.account_type       -- Customer account classification; answers: What is the tier/segment of the customer?
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE YEAR(t.transaction_date) = 2024
LIMIT 1000;
