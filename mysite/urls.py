from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("polls/", include("polls.urls")),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('', include('polls.urls')),
]

# Add this to serve uploaded media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# This only serves media in development mode. In production, you’ll serve it through Nginx or another server.
