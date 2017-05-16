# -*- coding: utf-8 -*-

from django.conf.urls import url

from djshop.apps.club.views import members as member_views
from djshop.apps.club.views import credit_card_references as credit_card_reference_views


urlpatterns = [
    url(r'^$', member_views.index, name="index"),
    url(r'^new/?$', member_views.new, name="new_member"),
    url(r'^(?P<member_id>\d+)/?$', member_views.view, name="view_member"),
    url(r'^(?P<member_id>\d+)/edit?$', member_views.edit, name="edit_member"),
    url(r'^(?P<member_id>\d+)/subscribe?$', member_views.subscribe, name="subscribe_member"),
    url(r'^(?P<member_id>\d+)/delete?$', member_views.delete, name="delete_member"),

    url(r'^(?P<member_id>\d+)/set_subscription_attributes?$', credit_card_reference_views.set_attributes, name="set_subscription_attributes"),

    url(r'^(?P<member_id>\d+)/(?P<reference_id>\d+)/confirm?$', credit_card_reference_views.confirm, name="confirm_subscription"),
    url(r'^(?P<sale_code>\d+)/ok?$', credit_card_reference_views.ok, name="subscription_ok"),
    url(r'^(?P<sale_code>\d+)/cancel?$', credit_card_reference_views.cancel, name="subscription_cancel")

]
