"""djshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin


from djshop.apps.public.views import index as index_views
from djshop.apps.public.views import sale as sale_views
from djshop.apps.club.views import credit_card_references as credit_card_references_views

urlpatterns = [
    url(r'^django_admin/', admin.site.urls),
    url(r'^store/', include('djshop.apps.store.urls', namespace="store")),
    url(r'^offers/', include('djshop.apps.offers.urls', namespace="offers")),
    url(r'^club/', include('djshop.apps.club.urls', namespace="club")),
    url(r'^public/', include('djshop.apps.public.urls', namespace="public")),
    url(r'^$', index_views.index, name="index"),
    # Payment URL
	url(r'^sale/confirmation/(?P<virtualpos_type>[a-z]+)$', sale_views.confirm_sale, name='payment_confirmation_url'),
	# Subscription confirm URL
	url(r'^subscription/confirmation/(?P<virtualpos_type>[a-z]+)$', credit_card_references_views.confirm, name='credit_card_references_views_url'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

