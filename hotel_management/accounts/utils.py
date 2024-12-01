from django.contrib.auth import authenticate, login


def login_user(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return user
    else:
        return None
