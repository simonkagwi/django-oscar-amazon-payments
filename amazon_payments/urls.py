from django.conf.urls import patterns, url

import views


# URLs for one-step checkout process
urlpatterns = patterns("",
    url(r'^amazon/login/$', views.AmazonOneStepLoginRedirectView.as_view(),  # noqa
        name='amazon-payments-login-onestep'),
    url(r'^amazon/$', views.AmazonOneStepPaymentDetailsView.as_view(),
        name='amazon-payments-onestep'),
)

# URLs for default oscar multi-step checkout process
urlpatterns += patterns("",
    url(r'^amazon2/login/$', views.AmazonLoginRedirectView.as_view(),  # noqa
        name='amazon-payments-login'),
    url(r'^amazon2/$', views.AmazonPaymentsIndexView.as_view(),
        name='amazon-payments-index'),
    url(r'^amazon2/shipping-address/$',
        views.AmazonShippingAddressView.as_view(),
        name='amazon-payments-shipping-address'),
    url(r'^amazon2/shipping-method/$',
        views.AmazonShippingMethodView.as_view(),
        name='amazon-payments-shipping-method'),
    url(r'^amazon2/payment-method/$', views.AmazonPaymentMethodView.as_view(),
        name='amazon-payments-payment-method'),
    url(r'^amazon2/preview/$',
        views.AmazonPaymentDetailsView.as_view(preview=True),
        name='amazon-payments-preview'),
    url(r'^amazon2/payment-details/$',
        views.AmazonPaymentDetailsView.as_view(),
        name='amazon-payments-payment-details'),
)
