from django.contrib import admin
from django.urls import path
# from .api import api
from ninja import NinjaAPI
from core.api import router as core_router
from django.conf import settings
from django.conf.urls.static import static

api = NinjaAPI(csrf=True)


api.add_router("/", core_router)  


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
