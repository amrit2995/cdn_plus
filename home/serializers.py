from rest_framework import serializers
from .models import CDN

class CDNSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    
    class Meta:
        model = CDN
        fields = ["name"]