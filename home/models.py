from django.db import models

# Create your models here.
class CDN(models.Model):
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self) -> str:
        return self.name