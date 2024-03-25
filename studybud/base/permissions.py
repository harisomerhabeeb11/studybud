from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from .views import *
from .models import *

def user_has_permission(request):
    # user will be in the request
    pass

def is_host(obj, model) -> bool:
    if obj.user != model.host:
        return False
    return True