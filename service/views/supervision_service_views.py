# rest
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
# models
from ..models.supervision_service_model import SupervisionService
# serializers
from ..serializers.supervision_service_serializer import SupervisionServiceSerializer
# permissions
# utile
from utils.api_exceptions import PermissionError
from utils.notification import notify_admins

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
class SupervisionServiceViewSet(viewsets.ModelViewSet):
    serializer_class = SupervisionServiceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = []
    lookup_field = 'uuid'

    def get_queryset(self):
        if self.request.user.is_authenticated and hasattr(self.request.user, 'customer'):
            return SupervisionService.objects.filter(customer=self.request.user.customer).order_by('-created_at')
        else:
            return SupervisionService.objects.all().order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'customer'):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بعملية الإنشاء هذه.')
        message = f'the user {request.user} has created a supervision service'
        notify_admins(sender=request.user, message=message)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if (not request.user.is_authenticated) or (not hasattr(request.user, 'customer')) or (instance.customer != request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بهذه العملية.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if (not request.user.is_authenticated) or (not hasattr(request.user, 'customer')) or (instance.customer != request.user.customer):
            raise PermissionError(en_message='You do not have permission to perform this action.', ar_message='ليس لديك الصلاحيات للقيام بهذه العملية.')
        return super().destroy(request, *args, **kwargs)