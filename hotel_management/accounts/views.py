from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from .forms import RegistrationForm
from .services import ProfileService, UserService
from .utils import login_user


@require_GET
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect("homepage")


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("homepage")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = login_user(request, username, password)

            if user:
                messages.success(request, f"You was successfully logged in")
                return redirect("homepage")
            else:
                messages.error(
                    request, "Authentication failed. Please check your credentials."
                )
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request, "user_login.html", {"authentication_form": form})


@require_http_methods(["GET", "POST"])
def register_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = RegistrationForm(request.POST)

            if form.is_valid():
                try:
                    UserService.create_user_with_sql(form.cleaned_data)
                    username = form.cleaned_data["username"]
                    password = form.cleaned_data["password1"]
                    messages.success(request, f"Account was created successfully")
                    user = login_user(request, username, password)

                    if user:
                        messages.success(request, f"You was successfully logged in")
                        return redirect("homepage")
                    else:
                        messages.error(
                            request,
                            "Authentication failed. Please check your credentials",
                        )
                        return redirect("login")
                except Exception as e:
                    messages.error(request, "Account wasn't created")
                    messages.error(request, str(e))
            else:
                messages.error(
                    request, "Account wasn't created. Please correct the errors below"
                )
            return render(request, "register.html", {"register_form": form})
        else:
            form = RegistrationForm()
        return render(request, "register.html", {"register_form": form})
    else:
        return redirect("homepage")


@login_required
def profile_view(request):
    user_id = request.user.id

    profile_data = ProfileService.get_profile(user_id)

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone_number = request.POST.get("phone_number")

        ProfileService.update_profile(user_id, first_name, last_name, phone_number)
        messages.success(request, "Profile was updated successfully")
        redirect("profile")
    return render(
        request,
        "profile.html",
        {
            "profile_data": profile_data,
        },
    )
