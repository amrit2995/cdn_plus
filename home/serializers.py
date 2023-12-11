from rest_framework import serializers
from .models import Distribution

class DistributionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50)
    
    class Meta:
        model = Distribution
        # fields = ["name", "provider", "status", "origin_server", "ssl_tls_config", "caching_policy"]
        fields = '__all__'