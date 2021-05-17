from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .functions import region, industry as fun_industry

BASE_URL = "http://localhost:8000/"


class GetRegionEmissionGas(APIView):
    """
    입력값 : 년도, 지역
    해당 년도와 지역대비 전체 온실 배출량 비교
    ex) 결과값(JSON) :
    "result" : 2018년도 전국 온실가스(349,791,382 [GHG]) 대비 서울는 0.56%의 온실가스(1,955,912[GHG])를 배출하고 있습니다."
    "media_url" : http://domain.com/media/region_total_usems_qnty_2018_서울.png"
    """

    def get(self, request):
        year = request.data.get("year")
        if not year:
            return JsonResponse(
                {"err_message": "Key Error from year"}, status.HTTP_400_BAD_REQUEST
            )
        location_name = request.data.get("location_name")
        if not location_name:
            return JsonResponse(
                {"err_message": "Key Error from location_name"},
                status.HTTP_400_BAD_REQUEST,
            )
        try:
            result = region.total_usems_qnty(year, location_name)
        except ValueError:
            return JsonResponse(
                {"err_message": "Fail to get data from open API."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not result:
            return JsonResponse(
                {"err_message": "Err Occurred. Please Try Again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = (
            f"{BASE_URL}media/region_total_usems_qnty_{year}_{location_name}.png"
        )
        return JsonResponse({"result": result, "media_url": media_url})


class GetEmissionGasCompareFromOther(APIView):
    """
    입력값 : 년도, 지역, 사용량
    해당 업체가 속해있는 지역의 전체 사용량과 업체 사용량 분석 비교
    예시 : 결과값(JSON)
    "result": "전남 지역 총 (78,516,261[GHG]) 온실가스 중 해당 업체는 온실가스(583,972[GHG]) 배출하고 있습니다."
    "media_url" : "http://domain.com/media/region_industry_usems_qnty_2017_전남.png"
    """

    def get(self, request):
        year = request.data.get("year")
        if not year:
            return JsonResponse(
                {"err_message": "Key Error from year"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        location_name = request.data.get("location_name")
        if not location_name:
            return JsonResponse(
                {"err_message": "Key Error from location_name"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        usage = request.data.get("usage")
        if not usage:
            return JsonResponse(
                {"err_message": "Key Error from usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = region.industry_usems_qnty_statistics(year, location_name, usage)
        if not result:
            return JsonResponse(
                {"err_message": "Err Occurred. Please Try Again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = (
            f"{BASE_URL}media/region_industry_usems_qnty_{year}_{location_name}.png"
        )
        return JsonResponse({"result": result, "media_url": media_url})


class GetIndustryEmissionGasFromAll(APIView):
    """
    특정 연도의 전국 온실가스 배출량 중 해당 업종의 배출량 분석 결과
    입력값 : 해당년도, 산업, GHG
    "result" : "2018년도 국내 업종 총 온실가스(698,909,140 [GHG]) 대비 현재 광업 업종은 0.10%의 온실가스(673,625[GHG])를 배출하고 있습니다."
    "media_url" : "http://domain.com/media/industry_total_usems_qnty_2018_광업.png
    """

    def get(self, request):
        year = request.data.get("year")
        if not year:
            return JsonResponse(
                {"err_message": "Key Error from year"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        industry = request.data.get("industry")
        if not industry:
            return JsonResponse(
                {"err_message": "Key Error from industry"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = fun_industry.total_usems_qnty(year, industry, "GHG")
        if not result:
            return JsonResponse(
                {"err_message": "Err Occurred. Please Try Again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = f"{BASE_URL}media/industry_total_usems_qnty_{year}_{industry}.png"
        return JsonResponse({"result": result, "media_url": media_url})


class GetIndustryEmissionGasFromSameAll(APIView):
    """
    특정 연도의 해당 업체에 해당하는 업종의 온실가스 배출량 중 해당업체의 사용량 분석 결과
    입력값 : 해당년도, 산업, 사용량, GHG
    "result" : "광업 업종 총 (673,625[GHG]) 온실가스 중 해당 업체는 온실가스(130,002[GHG]) 배출하고 있습니다."
    "media_url" : "http://domain.com/media/my_industry_usems_qnty_2018_광업.png
    """

    def get(self, request):
        year = request.data.get("year")
        if not year:
            return JsonResponse(
                {"err_message": "Key Error from year"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        industry = request.data.get("industry")
        if not industry:
            return JsonResponse(
                {"err_message": "Key Error from industry"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        usage = request.data.get("usage")
        if not usage:
            return JsonResponse(
                {"err_message": "Key Error from usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = fun_industry.industry_usems_qnty_statistics(
            year, industry, usage, "GHG"
        )
        if not result:
            return JsonResponse(
                {"err_message": "Err Occurred. Please Try Again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = f"{BASE_URL}media/my_industry_usems_qnty_{year}_{industry}.png"
        return JsonResponse({"result": result, "media_url": media_url})


class GetIndustryEnergyCompareDetail(APIView):
    """
    특정 연도의 해당 업체에 해당하는 업종의 각 에너지 종류별 사용량 대한 분석 결과
    입력값: 해당 년도, 산업, 가스, 기타, 석유류, 석탄류, 열에너지, 전력
    "media_url" : "http://domain.com/media/items_usems_qnty_statistics_2018_광업.png
    """

    def get(self, request):
        year = request.data.get("year")
        if not year:
            return JsonResponse(
                {"err_message": "Key Error from year"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        industry = request.data.get("industry")
        if not industry:
            return JsonResponse(
                {"err_message": "Key Error from industry"},
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
        result = fun_industry.items_usems_qnty_statistics(
            year, industry, gas, other, oil, coal, thermal, electric, "GHG"
        )
        if not result:
            return JsonResponse(
                {"err_message": "Err Occurred. Please Try Again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        media_url = f"{BASE_URL}media/items_usems_qnty_statistics_{year}_{industry}.png"
        return JsonResponse({"result": result, "media_url": media_url})
