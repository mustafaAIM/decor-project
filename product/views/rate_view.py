# rest framework
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
# models
from ..models.rate_model import Rate 
# serializers
from ..serializers.rate_serializer import RateSerializer

class RateViewSet(viewsets.ModelViewSet):
    queryset = Rate.objects.all()
    serializer_class = RateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)