#rest 
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.generics import CreateAPIView
#serializers 
from authentication.serializers import RegisterSerializer

class Register(CreateAPIView):
  serializer_class = RegisterSerializer
  def post(self, request, *args, **kwargs):
      user_data = request.data
      serialized_data = self.get_serializer(data = user_data)
      serialized_data.is_valid(raise_exception=True)
      serialized_data.save()
      return Response(serialized_data.data,HTTP_201_CREATED)