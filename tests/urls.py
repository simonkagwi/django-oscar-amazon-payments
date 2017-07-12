from django.conf.urls import include, url, patterns
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from oscar.app import shop
from oscar.views import handler500, handler404, handler403  # noqa

admin.autodiscover()

urlpatterns = patterns('',
    # Include admin as convenience. It's unsupported and you should
    # use the dashboard
    url(r'^admin/', include(admin.site.urls)),  # noqa
    # i18n URLS need to live outside of i18n_patterns scope of the shop
    url(r'^i18n/', include('django.conf.urls.i18n')),
    # Oscar's normal URLs
    url(r'', include(shop.urls)),
)
