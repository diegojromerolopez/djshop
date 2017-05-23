
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from djshop.apps.base.forms import DeleteForm


# Creation of object
def new(request, instance, form_class, template_path, ok_url):

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(ok_url)
    else:
        form = form_class(instance=instance)

    return render(request, template_path, {"form": form, "instance": instance})


# Edition of object
def edit(request, instance, form_class, template_path, ok_url):
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(ok_url)
    else:
        form = form_class(instance=instance)

    return render(request, template_path, {"form": form, "instance": instance})


# Delete an object
def delete(request, instance, template_path="base/forms/delete.html", next_url=None):
    if request.method == "POST":
        form = DeleteForm(request.POST)

        if form.is_valid() and form.cleaned_data.get("confirmed"):
            instance.delete()
            if next_url is None:
                return HttpResponseRedirect(reverse("store:view_products"))
            return HttpResponseRedirect(next_url)

    else:
        form = DeleteForm()

    instance.meta_verbose_name = instance._meta.verbose_name
    return render(request, template_path, {"form": form, "instance": instance})
