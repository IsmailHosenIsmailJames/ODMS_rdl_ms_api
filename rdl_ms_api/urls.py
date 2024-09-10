
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('user_app.urls')),
    path('api/v1/attendance/', include('attendance_app.urls')),
    path('api/v1/reports/', include('report_app.urls')),
    path('api/v1/delivery/', include('delivery_app.urls')),
    path('api/v1/cash_collection/', include('collection_app.urls')),
    path('api/v1/customer_location/', include('customer_location_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
