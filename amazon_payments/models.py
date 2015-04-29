from django.db import models


class AmazonPaymentsSession(models.Model):
    billing_agreement_id = models.TextField()
    basket = models.OneToOneField("basket.Basket", blank=True, null=True)
    order = models.OneToOneField("order.Order", blank=True, null=True)
    order_reference_id = models.TextField(blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AmazonPaymentsTransaction(models.Model):
    session = models.ForeignKey(AmazonPaymentsSession,
                                related_name="transactions")
    request = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AmazonPaymentsAuthAttempt(models.Model):
    session = models.ForeignKey(AmazonPaymentsSession,
                                related_name="auth_attempts")
    authorization_id = models.TextField(blank=True, null=True)
    transaction = models.OneToOneField(AmazonPaymentsTransaction, blank=True,
                                       null=True)
    created_at = models.DateTimeField(auto_now_add=True)
