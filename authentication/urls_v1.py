from django.urls import path
#views
from authentication.views import *

urlpatterns = [
  path("register/",Register.as_view()),
]