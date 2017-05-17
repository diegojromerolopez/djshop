from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from djangovirtualpos.models import VirtualPointOfSale
from djshop.apps.base import views as base_views
from djshop.apps.club.forms import MemberForm
from djshop.apps.club.models import Member, CreditCardReference


# View members
@login_required
def index(request):
    members = Member.objects.all()
    return render(request, "club/members/index.html", {"members": members})


# New club member
@login_required
def new(request):
    member = Member()
    return base_views.new(request, instance=member, form_class=MemberForm,
                           template_path="club/members/new.html", ok_url=reverse("club:index"))


# Edition of member
@login_required
def edit(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    return base_views.edit(request, instance=member, form_class=MemberForm,
                           template_path="club/members/edit.html", ok_url=reverse("club:index"))


# View a member
@login_required
def view(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    return render(request, "club/members/view.html", {"member": member})


# Delete a member
@login_required
def delete(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    return base_views.delete(request, instance=member)


# Subscribe
@login_required
def subscribe(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    reference = CreditCardReference.new(member)

    virtual_point_of_sales = VirtualPointOfSale.objects.all()
    replacements = {
        "member": member,
        "reference": reference,
        "virtual_point_of_sales": virtual_point_of_sales,
        "url_ok": request.build_absolute_uri(reverse("club:subscription_ok", kwargs={"sale_code": reference.code})),
        "url_nok": request.build_absolute_uri(reverse("club:subscription_cancel", kwargs={"sale_code": reference.code})),
    }
    return render(request, "club/members/subscribe.html", replacements)