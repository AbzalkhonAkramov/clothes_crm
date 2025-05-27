from django.db import models

class PromoCode(models.Model):
    name = models.CharField(max_length=100, unique=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "promo_codes"
        verbose_name = "Promo Code"
        verbose_name_plural = "Promo Codes"


class PromoCodeUsage(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='promo_code_usages')
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'promo_code_usages'
        unique_together = ('promo_code', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.promo_code.name}"

    def increment_usage(self):
        if self.usage_count < self.promo_code.usage_limit:
            self.usage_count += 1
            self.save()
            return True
        return False
