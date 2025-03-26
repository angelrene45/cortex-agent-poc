
-- more than distinct 150 type of the part
select DISTINCT P_TYPE from SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.PART;

-- Create the database
CREATE DATABASE IF NOT EXISTS cortex_search_tutorial_db;

-- Create the warehouse
CREATE OR REPLACE WAREHOUSE cortex_search_tutorial_wh WITH
     WAREHOUSE_SIZE='X-SMALL'
     AUTO_SUSPEND = 120
     AUTO_RESUME = TRUE
     INITIALLY_SUSPENDED=TRUE;

-- Clone the table
CREATE TABLE cortex_search_tutorial_db.public.PART (
    P_PARTKEY NUMBER(38,0) PRIMARY KEY,  
    P_NAME VARCHAR(55) NOT NULL,         
    P_MFGR VARCHAR(25) NOT NULL,         
    P_BRAND VARCHAR(10) NOT NULL,        
    P_TYPE VARCHAR(25) NOT NULL,         
    P_SIZE NUMBER(38,0) NOT NULL,        
    P_CONTAINER VARCHAR(10) NOT NULL,    
    P_RETAILPRICE NUMBER(12,2) NOT NULL, 
    P_COMMENT VARCHAR(23) NULL           
);

insert overwrite into cortex_search_tutorial_db.public.PART
select * from SNOWFLAKE_SAMPLE_DATA.TPCH_SF1.PART;


-- Create the Cortex Search Service from the cloned table (shared table is not supported in Cortex Search)
CREATE OR REPLACE CORTEX SEARCH SERVICE cortex_search_tutorial_db.public.my_part_types_search_service
  ON P_TYPE
  WAREHOUSE = cortex_search_tutorial_wh
  TARGET_LAG = '1 hour'
  AS (
      SELECT DISTINCT P_TYPE FROM cortex_search_tutorial_db.public.PART
  );


-- Testing Cortex Search
SELECT PARSE_JSON(
  SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
      'cortex_search_tutorial_db.public.my_part_types_search_service',
      '{
        "query": "BURNISHED COPPER",
        "limit": 5
      }'
  )
)['results'] as results;
