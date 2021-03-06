from django.conf.urls import url
from django.urls.conf import include, path
from .views import (
    GetEmissionGasCompareFromOther,
    GetIndustryEmissionGasFromAll,
    GetIndustryEmissionGasFromSameAll,
    GetIndustryEnergyCompareDetail,
    GetRegionEmissionGas,
    GetTotalEnergyFromNumber,
    GetPredictGraph
)

urlpatterns = [
    path("get/number", GetTotalEnergyFromNumber.as_view(), name='get_business_number'),
    path("compare/region", GetRegionEmissionGas.as_view(), name="get_location_comapre"),
    path(
        "compare/same-region",
        GetEmissionGasCompareFromOther.as_view(),
        name="get_same_region_compare",
    ),
    path(
        "compare/industry-all",
        GetIndustryEmissionGasFromAll.as_view(),
        name="get_compare_all",
    ),
    path(
        "compare/industry-sameall",
        GetIndustryEmissionGasFromSameAll.as_view(),
        name="get_compare_same_industry_all",
    ),
    path(
        "detail/industry-energy",
        GetIndustryEnergyCompareDetail.as_view(),
        name="get_industry_engergy_detail",
    ),
    path("get/predict-graph" ,GetPredictGraph.as_view(), name="get_predict_graph"),
]
