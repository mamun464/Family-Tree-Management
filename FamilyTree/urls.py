
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
#    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
   
   path('admin/', admin.site.urls),
   path('api/member/',include('FamilyApp.urls')),
   
#    path('api/events/',include('eventApp.urls')),
   
   
]
