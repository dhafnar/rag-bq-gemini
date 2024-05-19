# Serverless RAG with BigQuery and Gemini

## Description
This is a repo accompanying the Medium article of the same name.

For more information, refer to the article:
https://medium.com/@dhafnar/building-a-serverless-rag-system-with-bigquery-and-gemini-12e66328f622

## Folder Structure
- **bigquery**: Contains scripts and configurations related to BigQuery.
- **cloud_function**: Contains Google Cloud Functions code and deployment scripts.
- **frontend**: Contains the frontend application code.

## Setup Instructions
### BigQuery
Queries required for enabling vector search in BigQuery.

Four statements are within statements.sql.

One of the statements regarding indexing, is not needed for this excercise, but is needed for datasets
with over 5000 records.

To access the public dataset, you will need to create your dataset in US.

Make sure to replace references to my_project and my_dataset accordingly.

### Cloud Function
The code is for the cloud function v1 using Python 3.9.

The folder consists of main.py and requirements.txt.

Make sure to make the function publicly accessible and that it points to main.py. The rest of parameters can stay as default.

Make sure to replace references to my_project and my_dataset accordingly.

### Frontend
The frontend is a single HTML containing basic HTML, CSS and JS.

Make sure to assign the endpoint to the cloud function URL.