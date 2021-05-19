import pandas as pd
import datetime
from datas.functions.microdata import microdata_csv
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status, permissions
from .functions import region, industry as fun_industry
from accounts.models import Profile
from .models import Microdata

BASE_URL = "localhost:8000/"

class GetTotalEnergyFromNumber(APIView):
    def get(self, request):
        user = request.user
        year = 2018
        user_profile = user.profile
        if not user_profile:
            return JsonResponse(
                {"message": "Can't get profile from user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        business_number = user_profile.business_number
        if not business_number:
            return JsonResponse(
                {"message": "Key Error from business_number"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        use = 0
        for i in Microdata.objects.filter(fanm="CB60C1A3561DEFE46CE65C13E79C52041786F5DD").values('use'):
            use += float(i['use'])
        
        # df = list((Microdata.objects.filter(fanm="CB60C1A3561DEFE46CE65C13E79C52041786F5DD").values()))
        # print(df[0])
        # microdatas_list = list(microdatas)
        # print(microdatas_list)

        # a_list = list(a)
        # print(a)
        # microdata_ids = set(microdata.id for microdata in microdatas)
        # existing_question_microdatas = filter(lambda x: x.microdata.id not in microdatas_id, existing_question_microdatas)
        # print(existing_question_microdatas)
        return JsonResponse({"total_use" : use})
        # business_number = microdata


class GetRegionEmissionGas(APIView):
    """
     "datas/compare/region"
    지역대비 전체 온실 배출량 비교
    ex) 결과값(JSON) :
    "result" : 2018년도 전국 온실가스(349,791,382 [GHG]) 대비 서울는 0.56%의 온실가스(1,955,912[GHG])를 배출하고 있습니다."
    "media_url" : http://domain.com/media/region_total_usems_qnty_2018_서울.png"
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_profile = user.profile
        year = 2018
        if not user_profile:
            return JsonResponse(
                {"message": "Can't get profile from user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        location_name = user_profile.location_name
        if not location_name:
            return JsonResponse(
                {"message": "Key Error from location_name"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = region.total_usems_qnty(year, location_name)
        except ValueError:
            return JsonResponse(
                {"message": "Fail to get data from open API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = (
            f"{BASE_URL}media/region_total_usems_qnty_{year}_{location_name}.png"
        )
        return JsonResponse({"result": result, "media_url": media_url})


class GetEmissionGasCompareFromOther(APIView):
    """
    "datas/compare/same-region"
    입력값 : 사용량
    해당 업체가 속해있는 지역의 전체 사용량과 업체 사용량 분석 비교
    예시 : 결과값(JSON)
    "result": "전남 지역 총 (78,516,261[GHG]) 온실가스 중 해당 업체는 온실가스(583,972[GHG]) 배출하고 있습니다."
    "media_url" : "http://domain.com/media/region_industry_usems_qnty_2017_전남.png"
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_profile = user.profile
        year = 2018
        if not user_profile:
            return JsonResponse(
                {"message": "Can't get profile from user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        location_name = user_profile.location_name
        if not location_name:
            return JsonResponse(
                {"message": "Key Error from location_name"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        usage = request.data.get("usage")
        if not usage:
            return JsonResponse(
                {"message": "Key Error from usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = region.industry_usems_qnty_statistics(year, location_name, usage)
        except ValueError:
            return JsonResponse(
                {"message": "Fail to get data from open API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = (
            f"{BASE_URL}media/region_industry_usems_qnty_{year}_{location_name}.png"
        )
        return JsonResponse({"result": result, "media_url": media_url})


class GetIndustryEmissionGasFromAll(APIView):
    """
    "datas/compare/industry-all"
    특정 연도의 전국 온실가스 배출량 중 해당 업종의 배출량 분석 결과
    입력값 : 산업, GHG
    "result" : "2018년도 국내 업종 총 온실가스(698,909,140 [GHG]) 대비 현재 광업 업종은 0.10%의 온실가스(673,625[GHG])를 배출하고 있습니다."
    "media_url" : "http://domain.com/media/industry_total_usems_qnty_2018_광업.png
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        year = 2018
        user = request.user
        user_profile = user.profile
        if not user_profile:
            return JsonResponse(
                {"message": "Can't get profile from user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        industry = user_profile.industry
        if not industry:
            return JsonResponse(
                {"message": "Key Error from industry"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = fun_industry.total_usems_qnty(year, industry, "GHG")
        except ValueError:
            return JsonResponse(
                {"message": "Fail to get data from open API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = f"{BASE_URL}media/industry_total_usems_qnty_{year}_{industry}.png"
        return JsonResponse({"result": result, "media_url": media_url})


class GetIndustryEmissionGasFromSameAll(APIView):
    """
    "compare/industry-sameall"
    특정 연도의 해당 업체에 해당하는 업종의 온실가스 배출량 중 해당업체의 사용량 분석 결과
    입력값 : 사용량
    "result" : "광업 업종 총 (673,625[GHG]) 온실가스 중 해당 업체는 온실가스(130,002[GHG]) 배출하고 있습니다."
    "media_url" : "http://domain.com/media/my_industry_usems_qnty_2018_광업.png
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_profile = user.profile
        year = 2018
        if not user_profile:
            return JsonResponse(
                {"message": "Can't get profile from user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        industry = user_profile.industry
        if not industry:
            return JsonResponse(
                {"message": "Key Error from location_name"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        usage = request.data.get("usage")
        if not usage:
            return JsonResponse(
                {"message": "Key Error from usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = fun_industry.industry_usems_qnty_statistics(
                year, industry, usage, "GHG"
            )
        except ValueError:
            return JsonResponse(
                {"message": "Fail to get data from open API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if not result:
            return JsonResponse(
                {"message": "Err Occurred. Please Try Again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = f"{BASE_URL}media/my_industry_usems_qnty_{year}_{industry}.png"
        return JsonResponse({"result": result, "media_url": media_url})


class GetIndustryEnergyCompareDetail(APIView):
    """
    "detail/industry-energy"
    특정 연도의 해당 업체에 해당하는 업종의 각 에너지 종류별 사용량 대한 분석 결과
    입력값: 가스, 기타, 석유류, 석탄류, 열에너지, 전력
    "media_url" : "http://domain.com/media/items_usems_qnty_statistics_2018_광업.png
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        year = 2018
        user = request.user
        user_profile = user.profile
        if not user_profile:
            return JsonResponse(
                {"message": "Can't get profile from user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        industry = user_profile.industry
        if not industry:
            return JsonResponse(
                {"message": "Key Error from industry"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        gas = request.data.get("gas")
        if not gas:
            return JsonResponse(
                {"err_message": "Key Error from gas"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        other = request.data.get("other")
        if not other:
            return JsonResponse(
                {"err_message": "Key Error from other"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        oil = request.data.get("oil")
        if not oil:
            return JsonResponse(
                {"err_message": "Key Error from oil"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        coal = request.data.get("coal")
        if not coal:
            return JsonResponse(
                {"err_message": "Key Error from coal"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        thermal = request.data.get("thermal")
        if not thermal:
            return JsonResponse(
                {"err_message": "Key Error from thermal"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        electric = request.data.get("electric")
        if not electric:
            return JsonResponse(
                {"err_message": "Key Error from electric"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = fun_industry.items_usems_qnty_statistics(
                year, industry, gas, other, oil, coal, thermal, electric, "GHG"
            )
        except ValueError:
            return JsonResponse(
                {"err_message": "Fail to get data from open API."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = f"{BASE_URL}media/items_usems_qnty_statistics_{year}_{industry}.png"
        return JsonResponse({"result": result, "media_url": media_url})


class GetPredictGraph(APIView):
    def get(self, request):
        media_url = f"{BASE_URL}media/cod2_kr.png"
        return JsonResponse({"result": "Success!", "media_url": media_url})