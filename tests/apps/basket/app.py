from oscar.apps.basket.app import BasketApplication

from views import CustomBasketView


class CustomBasketApplication(BasketApplication):
    summary_view = CustomBasketView


application = CustomBasketApplication()
