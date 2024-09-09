
import json
import requests
import time
import boto3

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Image
from .serializers import ImageSerializer
from storefront import settings

s3_client = boto3.client(
  's3',
  aws_access_key_id=settings.S3_ACCESS_KEY_ID,
  aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
  region_name=settings.S3_REGION
)

class ImagesViewSet(viewsets.ModelViewSet):
  queryset = Image.objects.all().order_by("created_at")
  serializer_class = ImageSerializer
  permission_classes = [AllowAny]

  def get_queryset(self):
    return Image.objects.all().order_by("created_at")

  @csrf_exempt
  def create(self, request, *args, **kwargs):
    data = json.loads(request.body)
    inputs = data.get("prompt")

    response = requests.post(
      "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
      headers={"Authorization": f"Bearer {settings.HF_API_KEY}"},
      json={"inputs": inputs}
    )

    image_data = response.content

    filename = f"tmp/{inputs.replace(' ', '-').strip().lower()[:20]}-{int(time.time())}.jpg"

    s3_client.put_object(Bucket=settings.S3_BUCKET_NAME, Key=filename, Body=image_data)

    # with open(filename, 'wb') as f:
      # f.write(image_data)

    url = f"https://d36abtou431oro.cloudfront.net/{filename}"

    # return super().create(request, *args, **kwargs)
    return JsonResponse({'url': url}, status=200)