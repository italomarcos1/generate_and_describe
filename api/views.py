import os
import json
import requests
import time
import boto3

from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
hf_api_key = os.getenv("HF_API_KEY")
s3_access_key_id = os.getenv("S3_ACCESS_KEY_ID")
s3_secret_access_key = os.getenv("S3_SECRET_ACCESS_KEY")
s3_region = os.getenv("S3_REGION")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")

model = ChatOpenAI(model="gpt-4o",temperature="0.4",api_key=openai_api_key)
s3_client = boto3.client(
  's3',
  aws_access_key_id=s3_access_key_id,
  aws_secret_access_key=s3_secret_access_key,
  region_name=s3_region
)

def describe_persona(request):
  data = json.loads(request.body)
  query = data.get("query")

  prompt = f"""
    Objective: Analyze a given description text to extract the following attributes, if present: 'name,' 'nickname,' 'occupation,' 'age,' 'gender,' and 'country.' Ensure that no information is fabricated; only extract data explicitly mentioned in the text.
    Example: 
      Description: 'Julia, a Brazilian woman born in 1984, works as a software developer.'
      Extracted Attributes:

      Name: Julia
      Age: 40
      Occupation: Software Developer
      Gender: Woman
      Country: Brazil

    Note: If an attribute is not mentioned in the description, such as 'nickname' in the example above, return it as an empty string.
    Note: Given a location (city, state, district) try to infer the persona's country.
    Note: Given the name (and/or nickname) try to infer the persona's gender. IMPORTANT: only answer as 'M' or 'F'.

    ---

    INSTRUCTIONS: 'Respond with a valid JSON object, containing each of the provided fields as strings (and empty strings for non-existent fields)'

    JSON object for the aforementioned example: {{
      "name": "Julia",
      "age": "40",
      "occupation": "Software Developer",
      "gender": "Woman",
      "country": "Brazil",
      "nickname": ""
    }}

    ---

    Description (user input): {query}
    """
  
  json_schema = {
    "title": "personaDescription",
    "description": "Respond with a valid JSON object, containing each of the provided fields as strings (and empty strings for non-existent fields)",
    "type": "object",
    "properties": {
      "persona": {
        "type": "object",
        "description": "The setup of the joke",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name of the persona"
          },
          "age": {
            "type": "string",
            "description": "Age of the persona"
          },
          "occupation": {
            "type": "string",
            "description": "Occupation or job of the persona"
          },
          "gender": {
            "type": "string",
            "description": "Gender of the persona"
          },
          "country": {
            "type": "string",
            "description": "Country where the persona was born"
          },
          "nickname": {
            "type": "string",
            "description": "Nickname or common name used for the persona"
          },
        }
      },
    },
    "required": ["persona"],
  }
  
  structured_model = model.with_structured_output(json_schema)

  answer = structured_model.invoke(prompt)

  return JsonResponse(answer, status=200)

@csrf_exempt
def generate_image_old(request):
  data = json.loads(request.body)
  inputs = data.get("prompt")

  response = requests.post(
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
    headers={"Authorization": f"Bearer {hf_api_key}"},
    json={"inputs": inputs}
  )

  image_data = response.content

  filename = f"tmp/{inputs.replace(' ', '-').strip().lower()[:20]}-{int(time.time())}.jpg"

  s3_client.put_object(Bucket=s3_bucket_name, Key=filename, Body=image_data)

  # with open(filename, 'wb') as f:
    # f.write(image_data)

  url = f"https://d36abtou431oro.cloudfront.net/{filename}"

  return JsonResponse({'url': url}, status=200)