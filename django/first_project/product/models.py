from django.db import models
from category.models import Category   # import từ app category

class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'Còn hàng'),
        ('out_of_stock', 'Hết hàng'),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
    )
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return f"Ảnh của {self.product.name}"
