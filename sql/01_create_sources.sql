-- Creates the raw source tables used by the Customer 360 pipeline.
--
-- The script reads each worksheet from the Excel workbook and materializes it
-- as a DuckDB table so downstream models can query normalized sources.

-- Installs and loads the extensions required to read Excel files.
INSTALL spatial;
INSTALL excel;
LOAD excel;

-- Creates one raw table per business entity from the source workbook.
CREATE OR REPLACE TABLE customers AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Customers');

CREATE OR REPLACE TABLE accounts AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Accounts');

CREATE OR REPLACE TABLE transactions AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Transactions');

CREATE OR REPLACE TABLE loans AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Loans');

CREATE OR REPLACE TABLE cards AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Cards');

CREATE OR REPLACE TABLE branches AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Branches');

CREATE OR REPLACE TABLE channels AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Channels');

CREATE OR REPLACE TABLE interactions AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Interactions');

CREATE OR REPLACE TABLE complaints AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Complaints');

CREATE OR REPLACE TABLE offers AS
SELECT * FROM read_xlsx('data/starter_dataset.xlsx', sheet = 'Offers');
