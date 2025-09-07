from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("chat/", include("chatbot.urls")),
    path('store/', include('store.urls')),  # your store app
    path('', RedirectView.as_view(url='/store/', permanent=False)),
    path('', include('django.contrib.auth.urls')),
    path("accounts/", include("django.contrib.auth.urls")),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
