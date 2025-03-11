#models
from authentication.models import User
class ProfileService:
    def __init__(self):
        self.model = User.objects

    def update_profile(self, user: User, profile_data: dict) -> User:
        """Update user profile"""
        if 'image' in profile_data and user.image:
            user.image.delete(save=False)
        
        for key, value in profile_data.items():
            setattr(user, key, value)
        user.save()
        return user