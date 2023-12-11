from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import DistributionList, DistributionDetail

urlpatterns = [
    path('dis/', DistributionList.as_view(), name="get_distributions"),
    path('dis/<int:pk>', DistributionDetail.as_view(), name="distribution_detail_by_id"),
    # path('dis/<name>', DistributionDetail.as_view(), name="distribution_detail_by_name"),
]

urlpatterns = format_suffix_patterns(urlpatterns)