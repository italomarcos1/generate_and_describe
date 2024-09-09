import json
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from langchain_openai import ChatOpenAI
from storefront import settings

from .models import Persona
from .serializers import PersonaSerializer

model = ChatOpenAI(model="gpt-4o",temperature="0.4",api_key=settings.OPENAI_API_KEY)

class PersonaViewSet(viewsets.ModelViewSet):
  queryset = Persona.objects.all().order_by("created_at")
  serializer_class = PersonaSerializer
  permission_classes = [permissions.AllowAny]

  def create(self, request, *args, **kwargs):
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
