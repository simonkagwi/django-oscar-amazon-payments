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

if settings.DEBUG:
    import debug_toolbar

    # Server statics and uploaded media
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    # Allow error pages to be tested
    urlpatterns += patterns('',
        url(r'^403$', handler403),  # noqa
        url(r'^404$', handler404),
        url(r'^500$', handler500),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
