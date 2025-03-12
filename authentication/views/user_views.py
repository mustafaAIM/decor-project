#rest 
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
#serializers 
from authentication.serializers import *
from customer.serializers import *
#services
from authentication.services import OTPService
#ResponseFormatter

from core.utils.messages import ResponseFormatter



class RegisterViewSet(ViewSet):
  serializer_class = RegisterSerializer
  
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.otp_service = OTPService()

  def create(self, request, *args, **kwargs):
      user_data = request.data
      serialized_data = RegisterSerializer(data = user_data)
      serialized_data.is_valid(raise_exception=True)
      serialized_data.save() 
      return ResponseFormatter.success_response(
        data=serialized_data.data,
        message={"en":"User created successfully","ar":"تم إنشاء المستخدم بنجاح"},
        status_code=HTTP_201_CREATED
      )
  

  @action(detail="False" , methods=["POST"])
  def resend(self, request, *args,**kwargs):
     email = request.data.get("email")
     self.otp_service.set_strategy('email_verification')
     self.otp_service.resend_otp(email)
     return ResponseFormatter.success_response(
        message={"en":"OTP Sent","ar":"تم إرسال الرمز"},
        status_code=HTTP_200_OK
     )
     

  @action(detail=False, methods=['post'])
  def verify(self, request, *args, **kwargs):
        serializerd_data = OTPVerificationSerializer(data = request.data)
        serializerd_data.is_valid(raise_exception=True)
        user = User.objects.get(email = request.data.get("email"))
        serialized_customer = CustomerSerializer(data = {"user":user.id})
        serialized_customer.is_valid(raise_exception=True)
        serialized_customer.save()
        return ResponseFormatter.success_response(
          message={"en":"Email verified","ar":"تم التحقق من الايميل"},
          status_code=HTTP_200_OK
        )
      

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return ResponseFormatter.success_response(
          message={"en":"OTP Sent","ar":"تم إرسال الرمز"},
          status_code=HTTP_200_OK
        )

class PasswordResetVerifyOTPView(APIView):
    def post(self, request):
        serializer = PasswordResetVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return ResponseFormatter.success_response(
          message={"en":"OTP verified. Please enter your new password.","ar":"تم التأكد من الرمز، الرجاء ادخال كلمة المرور الجديدة"},
          status_code=HTTP_200_OK
       )

class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ResponseFormatter.success_response(
          message={"en":"Password has been reset successfully.","ar":"تم إعادة تعيين كلمة المرور بنجاح"},
          status_code=HTTP_200_OK
        )