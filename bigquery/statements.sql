# This statement creates a remote connection the required MODEL
CREATE OR REPLACE MODEL
  `my_project.my_dataset.textembedding`
REMOTE WITH CONNECTION `us.vertex_connection`
OPTIONS (ENDPOINT = 'textembedding-gecko@003');


# This statement copies the BBC dataset and creates vector embeddings
CREATE OR REPLACE TABLE
  my_dataset.bbc_searchable AS
SELECT
  content,
  title,
  ml_generate_embedding_result
FROM
  ML.GENERATE_EMBEDDING( MODEL `my_project.my_dataset.textembedding`,
    (
    SELECT
      body AS content,
      title
    FROM
      `bigquery-public-data.bbc_news.fulltext`
    GROUP BY
      body,
      title),
    STRUCT (TRUE AS flatten_json_output,
      'SEMANTIC_SIMILARITY' AS task_type) );


# OPTIONAL - If your table contains more than 5000 rows (BBC articles doesn't)
# you can create indexes using this query
CREATE OR REPLACE VECTOR INDEX `vector_index`
ON `my_project.my_dataset.bbc_searchable` (ml_generate_embedding_result)
OPTIONS(
      distance_type='COSINE', index_type='IVF', ivf_options='{"num_lists":10}' )



# This statement performs vector search
SELECT
  base.title,
  base.content
FROM
  VECTOR_SEARCH( TABLE `my_project.my_dataset.bbc_searchable`,
    'ml_generate_embedding_result',
    (
    SELECT
      ml_generate_embedding_result AS embedding_col
    FROM
      ML.GENERATE_EMBEDDING (MODEL `my_project.my_dataset.textembedding`,
        (
        SELECT
          "what did it say about Slovenia" AS content),
        STRUCT (TRUE AS flatten_json_output) )),
    top_k => 5 );