from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import CDNList, CDNDetail

urlpatterns = [
    path('cdns/', CDNList.as_view(), name="get_cdns"),
    path('cdns/<str:name>', CDNDetail.as_view(), name="cdn_detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)