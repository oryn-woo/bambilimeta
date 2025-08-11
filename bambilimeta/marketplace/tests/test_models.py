from django.test import TestCase
from bambilimeta.marketplace.models import Product
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bambilimeta.settings')
django.setup()


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        """Sets up the test data for this TestCase.

        The setUpTestData method is called with each test method to setup the
        required fixture for the test. The default implementation of this
        method does nothing.

        This method is called before the test method is executed. It is not
        called if the test method uses a database fixture, or if the test is
        marked with the @expectedFailure decorator.

        """

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
        