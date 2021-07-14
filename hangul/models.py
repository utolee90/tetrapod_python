from django.conf import settings
from django.db import models

# Create your models here.

# 텍스트 입력 필드 - 하나로만 처리하자.
class Text(models.Model):
    text = models.TextField(blank=True)
    