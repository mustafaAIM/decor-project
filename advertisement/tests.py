from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .models import Advertisement
from authentication.models import User

# Create your tests here.

class AdvertisementModelTests(TestCase):
    def test_create_advertisement(self):
        ad = Advertisement.objects.create(
            title_en="Test Advertisement",
            description_en="This is a test advertisement"
        )
        self.assertEqual(ad.title_en, "Test Advertisement")
        self.assertTrue(ad.is_active)
        
class AdvertisementAPITests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass123!",
            role=User.Role.ADMIN,
            is_active=True
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.advertisement = Advertisement.objects.create(
            title_en="Test Advertisement",
            description_en="This is a test advertisement"
        )
        
    def test_get_all_advertisements(self):
        url = reverse('advertisement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_create_advertisement(self):
        url = reverse('advertisement-list')
        data = {
            "title_en": "New Advertisement",
            "description_en": "This is a new advertisement"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    # def test_toggle_active(self):
    #     url = reverse('advertisement-toggle-active', kwargs={'uuid': self.advertisement.uuid})
    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.advertisement.refresh_from_db()
    #     self.assertFalse(self.advertisement.is_active)
