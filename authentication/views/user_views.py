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

#utils 
from authentication.utils import * 
#django
from django.shortcuts import get_object_or_404
from django.utils import timezone

#tasks
from authentication.tasks import * 

#TODO add rate limit
class RegisterViewSet(ViewSet):
  serializer_class = RegisterSerializer
  
  def create(self, request, *args, **kwargs):
      user_data = request.data
      serialized_data = RegisterSerializer(data = user_data)
      serialized_data.is_valid(raise_exception=True)
      serialized_data.save()
      return Response(serialized_data.data,HTTP_201_CREATED)
  

  @action(detail="False" , methods=["POST"])
  def resend(self, request, *args,**kwargs):
     email = request.data.get("email")
     user = get_object_or_404(User, email=email)
     user.otp = generate_random_otp()
     user.otp_exp = timezone.now()
     user.save()
     send_verification_email_task.delay(email, user.otp)
     return Response(message("OTP Sent","تم إرسال الرمز","success"),HTTP_200_OK)
     

  #TODO response check
  @action(detail=False, methods=['post'])
  def verify(self, request, *args, **kwargs):
      serializerd_data = OTPVerificationSerializer(data = request.data)
      serializerd_data.is_valid(raise_exception=True)
      user = User.objects.get(email = request.data.get("email"))
      user.is_active = True
      serialized_customer = CustomerSerializer(data = {"user":user.id})
      serialized_customer.is_valid(raise_exception=True)
      serialized_customer.save()
      user.save()
      response = message("Email verified","تم التحقق من الايميل","OK")
      response["message"]["data"] = customer_serializer.data
      return Response(response,HTTP_200_OK)
  


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer