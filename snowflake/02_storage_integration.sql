-- ============================================
-- AWS S3 Storage Integration
-- ============================================

USE ROLE ACCOUNTADMIN;

CREATE STORAGE INTEGRATION IF NOT EXISTS STOCK_ANALYTICS_S3_INT
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = '<AWS_IAM_ROLE_ARN>'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://<S3_BUCKET_NAME>/'
    );

-- Review the integration configuration
DESC INTEGRATION STOCK_ANALYTICS_S3_INT;

-- ============================================
-- External Stage
-- ============================================

CREATE OR REPLACE STAGE STOCK_ANALYTICS.RAW.S3_STOCK_STAGE
    URL = 's3://<S3_BUCKET_NAME>/'
    STORAGE_INTEGRATION = STOCK_ANALYTICS_S3_INT;