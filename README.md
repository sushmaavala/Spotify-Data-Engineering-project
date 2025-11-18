This project is an end-to-end **Data Engineering Pipeline** built entirely on **AWS Cloud**.  
It ingests raw Spotify 2023 data, transforms it using AWS Glue (PySpark), stores optimized data in S3, creates metadata using Glue Data Catalog, queries it using Amazon Athena, and visualizes it using Amazon QuickSight.


## **Project Architecture**
Raw Data (CSV) → S3 (Staging Layer)
↓
AWS Glue (ETL: joins, filters, Parquet)
↓
S3 (Data Warehouse Layer - Parquet)
↓
Glue Crawler → Glue Data Catalog
↓
Athena (SQL Analytics)


# 1️ **Dataset Description**

**Spotify Dataset 2023**  
Original CSVs:
- albums.csv  
- artists.csv  
- spotify_data.csv  
- spotify_features.csv  
- tracks.csv  

After preprocessing, I reduced it to **three clean CSV files**:
- albums  
- artists  
- tracks  

**Examples of attributes:**
- Danceability  
- Energy  
- Valence  
- Artist followers  
- Album popularity  
- Track duration, mode, loudness  


# 2️ **AWS IAM Setup **

I followed AWS best practices:


Created an **IAM user** with fine-grained access  
Granted minimal required services:

- Amazon S3 Full Access  
- AWS Glue Full Access  
- Athena Full Access  


# 3️ **S3 Data Lake Design**

Created 1 bucket with 2 layers:

s3://spotify-etl-project/
├── staging/ (raw/preprocessed CSVs)
└── data-warehouse/ (transformed parquet files)



### Staging Layer  
Uploaded:
- albums.csv  
- artists.csv  
- tracks.csv  

### Data Warehouse Layer  
This is where Glue writes optimized Parquet files.



# 4️ **ETL Pipeline — AWS Glue**

Used **Glue Visual ETL** → AWS auto-generates PySpark script.

### **Transformation Steps**
1. Loaded albums, artists, and tracks as sources  
2. Joined:
   - **albums ↔ artists** on `artist_id`  
   - joined with **tracks** on `track_id`
3. Dropped duplicate fields  
4. Converted output to **Parquet + Snappy** (fast + cost-efficient)  
5. Saved transformed files to:
s3://spotify-etl-project/data-warehouse/



This produced ~16 Parquet files.

###  Why Parquet?
- Faster query performance  
- Columnar format  
- Highly compressed  
- Industry standard for analytics  



# 5️ **Glue Job Configuration**
- Glue version: **4.0**  
- Python version: **3.10**  
- Worker type:
  - g.1x (4 vCPU / 16GB RAM)  
- IAM Role: `glue_access_s3`



# 6️ **Issues I Faced & How I Fixed Them **

## Issue 1 — Glue job could NOT be saved  
**Error:**
iam:PassRole is not authorized



###  Cause  
Glue needs permission to *assume* the IAM role.

###  Fix  
Added inline policy to IAM user:

json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "arn:aws:iam::<account-id>:role/glue_access_s3"
}
 Issue 2 — Glue job failed because of CloudWatch
Error:


logs:PutLogEvents not authorized
Cause
Glue role missing CloudWatch Logs permissions.

Fix
Added permissions:

json
Copy code
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "*"
}
Or attached:

AWSGlueServiceRole

CloudWatchLogsFullAccess

7️ Glue Crawler → Metadata Layer
Configured a Glue Crawler pointing to:

arduino
Copy code
s3://spotify-etl-project/data-warehouse/
Crawler created:

Database: spotify_db

Table: data_warehouse

This metadata is stored in the Glue Data Catalog.
