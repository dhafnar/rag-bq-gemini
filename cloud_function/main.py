import vertexai
from markdown import markdown
from google.cloud import bigquery
from vertexai.preview.generative_models import GenerativeModel
import json
from typing import Dict, List

project_id = "my_project"
client = bigquery.Client(project_id)
vertexai.init(project=project_id)


def set_cors_headers(headers: Dict[str, str] = None) -> Dict[str, str]:
    """
    Set CORS headers for the response.
    """
    if headers is None:
        headers = {}
    headers['Access-Control-Allow-Origin'] = '*'
    headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    headers['Access-Control-Allow-Headers'] = 'Content-Type'
    headers['Access-Control-Max-Age'] = '3600'
    return headers


def get_data_from_bigquery(user_query: str, top_num: int) -> List[Dict[str, str]]:
    """
    Fetch data from BigQuery based on the user query and top number of results.
    """
    query = """
        SELECT base.title, base.content
        FROM VECTOR_SEARCH(
          TABLE `my_project.my_dataset.bbc_searchable`, 'ml_generate_embedding_result',
          (
            SELECT ml_generate_embedding_result as embedding_col
            FROM ML.GENERATE_EMBEDDING
            (
              MODEL `my_project.my_dataset.textembedding`,
              (SELECT @user_query as content),
              STRUCT(TRUE as flatten_json_output)
            )
          ),
          top_k => @top_num
        )
    """
    params = [
        bigquery.ScalarQueryParameter("user_query", "STRING", user_query),
        bigquery.ScalarQueryParameter("top_num", "INT64", top_num)
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=params)
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    data_list = []
    for row in results:
        data_list.append({"title": row.title, "content": row.content})

    return data_list


def generate_gemini_response(user_query: str, results_list: List[Dict[str, str]]) -> str:
    """
    Generate a response using the Gemini model based on the user query and search results.
    """
    model = GenerativeModel(model_name='gemini-1.5-pro-preview-0514',
                            generation_config={
                                "temperature": 0.0
                            },
                            system_instruction="You are helping with summarization of articles. Don't repeat the question. "
                                               "Be concise, stick to relevant points from the articles, don't add headlines."
                                               "Use tenses correctly given that it is now year 2024."
                                               "Make sure to consider only relevant articles. If it make sense, start "
                                               "the answer by noting the answer is based on data from the BBC articles. "
                                               "Note that articles are years old and out of chronological order."
                                               "If the answer is not in the data, say so.")
    prompt = f"###{user_query}###. Answer based solely on this data from BBC articles: {results_list}"
    gemini_response = markdown(model.generate_content(prompt).text)
    return gemini_response


def main(request):
    """
    Main entry point for the Cloud Function.
    """
    if request.method == 'OPTIONS':
        headers = set_cors_headers()
        return ('', 204, headers)

    request_json = request.get_json()
    user_query = request_json['user_query']
    top_num = request_json['top_num']

    # Fetch data from BigQuery
    results_list = get_data_from_bigquery(user_query, top_num)

    # Generate response using Gemini model
    gemini_response = generate_gemini_response(user_query, results_list)

    response_json = {
        "geminiResponse": gemini_response,
        "searchResults": results_list
    }

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    return (json.dumps(response_json), 200, headers)
