from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import House, HouseImage, HouseReview

User = get_user_model()


class HouseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.house = House.objects.create(
            title='Test House',
            owner=self.user,
            location='Test Location',
            price=100000.00,
            house_desc='A test house description'
        )

    def test_house_creation(self):
        self.assertEqual(self.house.title, 'Test House')
        self.assertEqual(self.house.owner.username, 'testuser')
        self.assertEqual(str(self.house), 'Test House')


class HouseReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        
        self.house = House.objects.create(
            title='Test House',
            owner=self.user,
            location='Test Location',
            price=100000.00,
            house_desc='A test house description'
        )
        
        self.review = HouseReview.objects.create(
            house=self.house,
            author=self.user,
            comment='Great house!',
            rating=5
        )
    
    def test_review_creation(self):
        self.assertEqual(self.review.house, self.house)
        self.assertEqual(self.review.author, self.user)
        self.assertEqual(self.review.rating, 5)
