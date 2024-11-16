#rest 
from rest_framework import serializers
#models 
from customer.models import *
class CustomerSerializer(serializers.ModelSerializer):
      class Meta:
            model = Customer
            fields = "__all__"