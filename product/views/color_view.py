# rest framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# models
from ..models.color_model import Color
# serializers
from ..serializers.color_serializer import ColorSerializer

class ColorListView(APIView):
    def get(self, request):
        colors = Color.objects.all()
        serializer = ColorSerializer(colors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)