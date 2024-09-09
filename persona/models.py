from django.db import models

# Create your models here.
class Persona(models.Model):
  name = models.CharField(max_length=100)
  age = models.IntegerField()
  occupation = models.CharField(max_length=100)
  gender = models.CharField(max_length=100)
  country = models.CharField(max_length=100)
  nickname = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    default_related_name = "personas"
    ordering = ["created_at"]

  def __str__(self) -> str:
    return str(self.name)