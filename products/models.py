from django.db import models


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('cleanser', 'Cleanser'), ('moisturizer', 'Moisturizer'),
        ('sunscreen', 'Sunscreen'), ('treatment', 'Treatment'),
        ('serum', 'Serum'), ('mask', 'Face Mask'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    skin_types = models.JSONField(default=list, help_text='List of skin types this product suits')
    conditions = models.JSONField(default=list, help_text='List of conditions this product helps')
    rating = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.brand}"
