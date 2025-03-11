from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from authentication.models import User
from django.utils import timezone
from datetime import timedelta
import time
from unittest.mock import patch

class UserRegistrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('authentication:v1:register')
        self.test_user_data = {
            "email": "test@example.com",
            "password": "tE@stpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }

    def test_register_user_successful(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.test_user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.test_user_data['email']).exists())
        
        user = User.objects.get(email=self.test_user_data['email'])
        self.assertEqual(user.first_name, self.test_user_data['first_name'])
        self.assertEqual(user.last_name, self.test_user_data['last_name'])
        self.assertEqual(user.phone, self.test_user_data['phone'])
        self.assertFalse(user.is_active)
        self.assertIsNotNone(user.otp)
        self.assertIsNotNone(user.otp_exp)

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = self.test_user_data.copy()
        del incomplete_data['email']
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        incomplete_data = self.test_user_data.copy()
        del incomplete_data['password']
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        incomplete_data = self.test_user_data.copy()
        del incomplete_data['first_name']
        response = self.client.post(self.register_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_email(self):
        """Test registration with invalid email format"""
        invalid_data = self.test_user_data.copy()
        invalid_data['email'] = "invalid-email"
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        response1 = self.client.post(self.register_url, self.test_user_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email=self.test_user_data['email'])
        user.is_active = True
        user.save()
        
        response2 = self.client.post(self.register_url, self.test_user_data, format='json')
        
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('authentication.services.auth_service.OTPService.send_otp')
    def test_otp_sent_on_register(self, mock_send_otp):
        """Test that OTP is sent when user registers"""
        self.client.post(self.register_url, self.test_user_data, format='json')
        mock_send_otp.assert_called_once()


class EmailVerificationTests(APITestCase):
    """Test email verification process"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('authentication:v1:register')
        self.verify_url = reverse('authentication:v1:verification')
        self.resend_url = reverse('authentication:v1:resend-otp')
        
        self.test_user_data = {
            "email": "test@example.com",
            "password": "tE@stpass123",
            "first_name": "Test",
            "last_name": "User",
            "phone": "1234567890"
        }
        
        data = self.client.post(self.register_url, self.test_user_data, format='json')
        print("DATA",data)
        self.test_user = User.objects.get(email=self.test_user_data['email'])

    def test_verify_email_successful(self):
        """Test successful email verification"""
        verification_data = {
            "email": self.test_user.email,
            "otp": self.test_user.otp
        }
        response = self.client.post(self.verify_url, verification_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)
        self.assertIsNone(self.test_user.otp)
        self.assertIsNone(self.test_user.otp_exp)

    def test_verify_email_wrong_otp(self):
        """Test email verification with wrong OTP"""
        verification_data = {
            "email": self.test_user.email,
            "otp": "000000"
        }
        response = self.client.post(self.verify_url, verification_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_active)

    def test_verify_email_expired_otp(self):
        """Test email verification with expired OTP"""
        self.test_user.otp_exp = timezone.now() - timedelta(minutes=15)
        self.test_user.save()
        
        verification_data = {
            "email": self.test_user.email,
            "otp": self.test_user.otp
        }
        response = self.client.post(self.verify_url, verification_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_active)

    def test_resend_otp(self):
        """Test resending OTP"""
        old_otp = self.test_user.otp
        
        resend_data = {"email": self.test_user.email}
        response = self.client.post(self.resend_url, resend_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.test_user.refresh_from_db()
        self.assertIsNotNone(self.test_user.otp)
        self.assertNotEqual(old_otp, self.test_user.otp)


class AuthenticationTests(APITestCase):
    """Test user authentication (login)"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('authentication:v1:login')
        
        self.verified_user = User.objects.create_user(
            email="verified@example.com",
            password="verifiedpass123",
            first_name="Verified",
            last_name="User",
            is_active=True
        )
        
        self.unverified_user = User.objects.create_user(
            email="unverified@example.com",
            password="unverifiedpass123",
            first_name="Unverified",
            last_name="User",
            is_active=False
        )

    def test_login_verified_user(self):
        """Test login with verified user"""
        login_data = {
            "email": "verified@example.com",
            "password": "verifiedpass123"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], "verified@example.com")
        self.assertEqual(response.data['role'], User.Role.CUSTOMER)

    def test_login_unverified_user(self):
        """Test login with unverified user"""
        login_data = {
            "email": "unverified@example.com",
            "password": "unverifiedpass123"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "verified@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordResetTests(APITestCase):
    """Test password reset flow"""
    
    def setUp(self):
        self.client = APIClient()
        self.reset_request_url = reverse('authentication:v1:password-reset-request')
        self.reset_verify_url = reverse('authentication:v1:password-reset-verify')
        self.reset_url = reverse('authentication:v1:password-reset')
        
        self.user = User.objects.create_user(
            email="user@example.com",
            password="userpass123",
            first_name="Test",
            last_name="User",
            is_active=True
        )

    @patch('authentication.services.password_service.OTPService.send_otp')
    def test_request_password_reset(self, mock_send_otp):
        """Test requesting a password reset"""
        reset_data = {"email": self.user.email}
        response = self.client.post(self.reset_request_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_otp.assert_called_once()

    def test_verify_password_reset_otp(self):
        """Test verifying OTP for password reset"""
        reset_data = {"email": self.user.email}
        self.client.post(self.reset_request_url, reset_data, format='json')
        
        self.user.refresh_from_db()
        otp = self.user.otp
        
        verify_data = {
            "email": self.user.email,
            "otp": otp
        }
        response = self.client.post(self.reset_verify_url, verify_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.otp)

    def test_reset_password(self):
        """Test actual password reset"""
        reset_data = {"email": self.user.email}
        self.client.post(self.reset_request_url, reset_data, format='json')
        
        self.user.refresh_from_db()
        otp = self.user.otp
        
        verify_data = {
            "email": self.user.email,
            "otp": otp
        }
        self.client.post(self.reset_verify_url, verify_data, format='json')
        
        new_password = "newpass456"
        reset_data = {
            "email": self.user.email,
            "new_password": new_password
        }
        response = self.client.post(self.reset_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        login_data = {
            "email": self.user.email,
            "password": new_password
        }
        login_response = self.client.post(reverse('authentication:v1:login'), login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)


class UserProfileTests(APITestCase):
    """Test user profile functionality"""
    
    def setUp(self):
        self.client = APIClient()
        self.profile_url = reverse('authentication:v1:user-profile')
        
        self.user = User.objects.create_user(
            email="profile@example.com",
            password="profilepass123",
            first_name="Profile",
            last_name="User",
            is_active=True
        )
        
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)
        self.assertEqual(response.data['last_name'], self.user.last_name)

    def test_update_profile(self):
        """Test updating user profile"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone": "9876543210",
            "address": "123 Test St"
        }
        response = self.client.patch(self.profile_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, update_data['first_name'])
        self.assertEqual(self.user.last_name, update_data['last_name'])
        self.assertEqual(self.user.phone, update_data['phone'])
        self.assertEqual(self.user.address, update_data['address'])

    def test_unauthorized_profile_access(self):
        """Test accessing profile without authentication"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OTPFunctionalityTests(APITestCase):
    """Test OTP-related functionality directly"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email="otp@example.com",
            password="otppass123",
            first_name="OTP",
            last_name="User",
            is_active=False
        )
        
        from authentication.services.otp_service import OTPService
        self.otp_service = OTPService()

    def test_otp_expiration(self):
        """Test OTP expiration logic"""
        self.user.otp_exp = timezone.now() - timedelta(minutes=15)
        self.user.otp = "123456"
        self.user.save()
        
        self.assertTrue(self.user.is_otp_expired())
        
        self.user.otp_exp = timezone.now() + timedelta(minutes=5)
        self.user.save()
        
        self.assertFalse(self.user.is_otp_expired())

    def test_strategy_pattern(self):
        """Test that different OTP strategies work correctly"""
        self.otp_service.set_strategy('email_verification')
        with patch('authentication.tasks.send_verification_email_task.delay') as mock_email_task:
            self.otp_service.send_otp(self.user.email)
            mock_email_task.assert_called_once()
        
        self.otp_service.set_strategy('password_reset')
        with patch('authentication.tasks.send_reset_password_verification_email_task.delay') as mock_reset_task:
            self.otp_service.send_otp(self.user.email)
            mock_reset_task.assert_called_once()