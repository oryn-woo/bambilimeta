from django.test import TestCase
from bambilimeta.marketplace.models import Product
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bambilimeta.settings')
django.setup()


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name="Test Product",
            price=19.99,
            description="A test product for unit testing.",
            stock=10,
        )

    def test_product_creation(self):
        self.assertEqual(Product.objects.count(), 1)

    def test_in_stock_property(self):
        self.assertTrue(self.product.stock > 0)

        self.product.stock = 0
        self.assertFalse(self.product.stock > 0)
        