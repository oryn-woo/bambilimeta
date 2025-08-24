import os
import tempfile
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io

from ..models import Product, ProductImage, Favorite
from ..forms import ProductForm, ImageInlineFormset

User = get_user_model()


def get_temporary_image(temp_file):
    """Helper function to create a test image"""
    size = (200, 200)
    color = (255, 0, 0, 0)
    image = Image.new("RGBA", size, color)
    image.save(temp_file, 'png')
    temp_file.seek(0)
    return temp_file


class ProductCreateViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.url = reverse('market:product-create')
        self.client.login(username='testuser', password='testpass123')
        
    def test_get_request_authenticated(self):
        """Test that authenticated user can access the create product page"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/product_form.html')
        self.assertIsInstance(response.context['form'], ProductForm)
        self.assertIn('formset', response.context)
        
    def test_redirect_if_not_logged_in(self):
        """Test that unauthenticated users are redirected to login"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
    def test_create_product_with_valid_data(self):
        """Test creating a product with valid data"""
        with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
            temp_file = get_temporary_image(temp_file)
            
            post_data = {
                'name': 'Test Product',
                'price': '19.99',
                'description': 'A test product',
                'stock': '10',
                'images-TOTAL_FORMS': '2',
                'images-INITIAL_FORMS': '0',
                'images-MIN_NUM_FORMS': '0',
                'images-MAX_NUM_FORMS': '1000',
                'images-0-image': SimpleUploadedFile(
                    name='test_image.png',
                    content=temp_file.read(),
                    content_type='image/png'
                ),
                'images-1-image': '',
            }
            
            response = self.client.post(self.url, post_data, follow=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Product.objects.count(), 1)
            self.assertEqual(ProductImage.objects.count(), 1)
            product = Product.objects.first()
            self.assertEqual(product.name, 'Test Product')
            self.assertEqual(product.seller, self.user)
            self.assertTrue(product.images.exists())


class ProductListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test user
        test_user = User.objects.create_user(username='testuser', password='testpass123')
        
        # Create test products
        number_of_products = 10
        for i in range(number_of_products):
            Product.objects.create(
                name=f'Product {i}',
                price=10.99 + i,
                stock=5 + i,
                description=f'Test product {i}',
                seller=test_user
            )
    
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/marketplace/')
        self.assertEqual(response.status_code, 200)
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('market:product-list'))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('market:product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/product_list.html')
        
    def test_lists_all_products(self):
        response = self.client.get(reverse('market:product-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('products' in response.context)
        self.assertEqual(len(response.context['products']), 10)


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.product = Product.objects.create(
            name='Test Product',
            price=19.99,
            stock=5,
            description='A test product',
            seller=self.user
        )
        
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/marketplace/product/{self.product.pk}/')
        self.assertEqual(response.status_code, 200)
        
    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('market:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('market:product-detail', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/product_detail.html')
        
    def test_product_detail_contains_correct_data(self):
        response = self.client.get(reverse('market:product-detail', kwargs={'pk': self.product.pk}))
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertContains(response, self.product.price)


class ToggleFavoriteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.product = Product.objects.create(
            name='Test Product',
            price=19.99,
            stock=5,
            description='A test product',
            seller=self.other_user
        )
        self.url = reverse('market:toggle-favorite', kwargs={'pk': self.product.pk})
        
    def test_toggle_favorite_requires_login(self):
        """Test that login is required to favorite a product"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)  # Redirects to login
        
    def test_add_favorite(self):
        """Test adding a product to favorites"""
        self.client.login(username='testuser', password='testpass123')
        
        # First request adds to favorites
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'added')
        self.assertTrue(Favorite.objects.filter(user=self.user, product=self.product).exists())
        
        # Second request removes from favorites
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'removed')
        self.assertFalse(Favorite.objects.filter(user=self.user, product=self.product).exists())
        
    def test_toggle_favorite_invalid_product(self):
        """Test toggling favorite for non-existent product"""
        self.client.login(username='testuser', password='testpass123')
        invalid_url = reverse('market:toggle-favorite', kwargs={'pk': 9999})
        response = self.client.post(invalid_url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)


class ProductImageEditViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.product = Product.objects.create(
            name='Test Product',
            price=19.99,
            stock=5,
            description='A test product',
            seller=self.user
        )
        self.url = reverse('market:product-image-edit', kwargs={'product_id': self.product.pk})
        self.client.login(username='testuser', password='testpass123')
        
    def test_get_request_authenticated_owner(self):
        """Test that product owner can access the image edit page"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace/product_image_upload.html')
        self.assertIn('formset', response.context)
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'], self.product)
        
    def test_upload_image(self):
        """Test uploading a new image to a product"""
        with tempfile.NamedTemporaryFile(suffix='.png') as temp_file:
            temp_file = get_temporary_image(temp_file)
            
            post_data = {
                'images-TOTAL_FORMS': '1',
                'images-INITIAL_FORMS': '0',
                'images-MIN_NUM_FORMS': '0',
                'images-MAX_NUM_FORMS': '1000',
                'images-0-image': SimpleUploadedFile(
                    name='test_image.png',
                    content=temp_file.read(),
                    content_type='image/png'
                ),
            }
            
            response = self.client.post(self.url, post_data, follow=True)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(ProductImage.objects.count(), 1)
            self.assertTrue(self.product.images.exists())
            
    def test_unauthorized_access(self):
        """Test that non-owners cannot access the image edit page"""
        # Create a different user
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # Forbidden


class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.product = Product.objects.create(
            name='Test Product',
            price=19.99,
            stock=5,
            description='A test product',
            seller=self.user
        )
        
    def test_product_creation(self):
        """Test product creation and string representation"""
        self.assertEqual(str(self.product), 'Test Product')
        self.assertEqual(self.product.seller, self.user)
        self.assertTrue(self.product.is_available)
        self.assertEqual(self.product.formatted_price, '$19.99')
        
    def test_product_properties(self):
        """Test product model properties"""
        self.assertTrue(self.product.valid_price)
        self.assertTrue(self.product.is_available)
        
        # Test is_new property
        self.assertTrue(self.product.is_new)  # Should be new as it was just created
        
        # Test get_absolute_url
        self.assertEqual(
            self.product.get_absolute_url(),
            reverse('market:product-detail', kwargs={'pk': self.product.pk})
        )
