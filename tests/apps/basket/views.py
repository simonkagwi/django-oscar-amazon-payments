from django.conf import settings

from oscar.apps.basket.views import BasketView


class CustomBasketView(BasketView):

    def get_context_data(self, *args, **kwargs):
        ctx = super(CustomBasketView, self).get_context_data(*args, **kwargs)
        ctx['amazon_payments_seller_id'] = settings.AMAZON_PAYMENTS_SELLER_ID
        ctx['amazon_payments_client_id'] = settings.AMAZON_PAYMENTS_CLIENT_ID
        ctx['amazon_payments_is_live'] = settings.AMAZON_PAYMENTS_IS_LIVE
        return ctx
