from oscar.apps.basket.abstract_models import AbstractBasket


class Basket(AbstractBasket):

    @property
    def has_subscriptions(self):
        return True


from oscar.apps.basket.models import *  # noqa
