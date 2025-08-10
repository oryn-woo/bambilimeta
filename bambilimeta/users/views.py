from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from .forms import UserUpdateForm, UserRegisterForm, ProfileUpdateForm, AdminProfileUpdateForm
from django.contrib.auth.decorators import login_required
from marketplace.models import Product

class Register(View):

    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        return render(request, "users/register.html", context={"form": form})

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            messages.success(request, message="Account created successful")
            return redirect("auth:login")
        return render(request, "users/register.html", context={"form": form})



@login_required
def profile(request):
    profile = request.user.profile
    FormClass = AdminProfileUpdateForm if request.user.is_staff or request.user.profile.role != 'regular' else ProfileUpdateForm

    if request.method == "POST":
        # Copy POSt so fields can be safely removed (prevent tampering)
        post = request.POST.copy()
        # If user is regular, remove any role included in POST
        if profile.role == "regular":
            post.pop("role", None)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = FormClass(post, request.FILES, instance=profile)
        # The image uploaded by user.


        if u_form.is_valid() and p_form.is_valid():
            # final enforcement: ensure regular user cannot escalate role
            if request.user.profile.role == "regular":
                p_form.instance.role = request.user.profile.role
            u_form.save()
            p_form.save()
            messages.success(request, message="Your account has been updated!.")
            return redirect("auth:profile")

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    # helpful flag for template: whether the 'role' field exists (so template shows it)
    show_role = 'role' in p_form.fields

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "products": Product.objects.all(),
        "show_role": show_role
    }
    return render(request, "users/index.html", context)
