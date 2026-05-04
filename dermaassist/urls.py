from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/users/', include('users.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/diagnosis/', include('diagnosis.urls')),
    path('api/history/', include('history.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/products/', include('products.urls')),
    path('api/admin-panel/', include('adminpanel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
