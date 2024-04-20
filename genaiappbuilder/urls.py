from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
import debug_toolbar

from core.views import ui_playground_view
from . import settings


urlpatterns = [
    path("admin/", admin.site.urls),
    path('uip/', ui_playground_view, name='ui_playground'),
    path('core/', include('core.urls')),
    path('genai_app/', include('genai_app.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('allauth.socialaccount.urls')),
    # Wagtail
    path("wagtail-admin/", include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('', include(wagtail_urls), name='dashboard'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += path("__debug__/", include(debug_toolbar.urls)),
