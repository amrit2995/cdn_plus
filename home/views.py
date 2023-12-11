from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
# from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins

from .models import Distribution
from .serializers import DistributionSerializer

class DistributionList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Delete all records in the Distribution model
        Distribution.objects.all().delete()
        return Response("All records deleted successfully.", status=status.HTTP_204_NO_CONTENT)

class DistributionDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)