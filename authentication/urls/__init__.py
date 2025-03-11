from django.urls import path, include

app_name = 'authentication'

urlpatterns = [
    path('v1/', include('authentication.urls.v1')),
]
