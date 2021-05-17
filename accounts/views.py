from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import *
from .serializers import *
from .permissions import *
from django.core.mail import EmailMessage

# Create your views here.


class SignUpRequestData(viewsets.ModelViewSet):
    serializer_class = SignUpRequestDataSerializer
    queryset = Profile.objects.all()
    http_method_names = ["get", "post"]
    permission_classes = (OnlyCanSeeAdminUser,)

    def create(self, request, *args, **kwargs):
        """
        Example
        business_number         사업장 번호
        business_name           사업장 이름
        officer_name            책임자 이름
        officer_phone           책임자 번호
        officer_position        책임자 직급
        officer_email           책임자 이메일
        location_name           지역
        industry                업종
        password                만들어지게 될 비밀번호

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # response = Response(
        #     serializer.data, status=status.HTTP_201_CREATED, headers=headers
        # )
        response = JsonResponse(
            {"message": "Registration Success! The administrator will contact soon"},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
        return response

    def list(self, request, *args, **kwargs):
        """
        신청서 리스트 가져오기
        """
        return super().list(request, *args, **kwargs)


# return JsonResponse
class SignUpRequestAccept(APIView):
    def post(self, request):
        profile_pk = request.data.get("profile_pk")
        try:
            profile = Profile.objects.get(id=profile_pk)
        except Profile.DoesNotExist:
            return JsonResponse(
                {"err_message": "Object Profile Not Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        isprofile = profile.profile_fk.first()
        if isprofile:
            return JsonResponse(
                {"err_message": "Profile Already Registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile_email = profile.officer_email
        password = profile.password
        user = User.objects.create(email=profile_email, profile=profile)
        if not user:
            return JsonResponse(
                {"err_message": "Error When Creating User"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password)
        user.save()
        subject = "환경메이트 가입 완료 안내"
        message = f"보내주신 정보를 바탕으로 인증이 진행되었으며, 회원가입이 완료되었습니다."
        try:
            mail = EmailMessage(subject, message, to=[profile_email])
            mail.send()
        except:
            return JsonResponse(
                {"err_message": "Error Occurred When Sending Mail"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile.password = "1111"
        profile.save()
        return JsonResponse({"message": "User Created"}, status=status.HTTP_201_CREATED)


class TestView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return JsonResponse({"Message": "Test Success!"})
