# This file stores all SQL queries used in this project

CREATE_FOREX_SCHEMA = "CREATE SCHEMA IF NOT EXISTS forex;"

CREATE_MAIN_TABLE = """
    CREATE TABLE IF NOT EXISTS forex.binary_options_historical_quotes (
        quote_sk BIGINT IDENTITY (0, 1),
        date_seconds TIMESTAMP,
        active_id INT,
        value NUMERIC (10, 6),
        PRIMARY KEY (quote_sk)
    );
"""

CREATE_ACTIVE_DIM_TABLE = """
    DROP TABLE IF EXISTS forex.dim_active_id;
    CREATE TABLE IF NOT EXISTS forex.dim_active_id (
    active_id INT,
    active_name TEXT,
    PRIMARY KEY (active_id)
    );
"""

CREATE_INDEX_TABLE = """
    DROP TABLE IF EXISTS forex.financial_index;
    CREATE TABLE IF NOT EXISTS forex.financial_index (
    date_index_sk INT IDENTITY (0, 1),
    date DATE,
    high NUMERIC (20,6),
    low NUMERIC (20,6),
    "open" NUMERIC (20,6),
    close NUMERIC (20,6),
    volume NUMERIC (20,6),
    country TEXT,
    PRIMARY KEY (date_index_sk)
"""

INSERT_ACTIVE_DIM_TABLE = """
    INSERT INTO forex.dim_active_id VALUES
    (1, 'EUR/USD'),
    (2, 'EUR/GBP'),
    (3, 'GBP/JPY'),
    (4, 'EUR/JPY'),
    (5, 'GBP/USD'),
    (6, 'USD/JPY');
"""
