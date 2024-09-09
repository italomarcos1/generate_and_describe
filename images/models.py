from django.db import models

class Image(models.Model):
  name = models.CharField(max_length=100)
  url = models.CharField(max_length=100, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    default_related_name = "images"
    ordering = ["created_at"]

  def __str__(self) -> str:
    return self.name