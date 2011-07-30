from django.contrib import admin
from django.conf.urls.defaults import patterns, include, url
from django.conf import settings


admin.autodiscover()


urlpatterns = patterns('',
    # Serve static media
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),

    url(r'^', include('core.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^game/', include('game.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
