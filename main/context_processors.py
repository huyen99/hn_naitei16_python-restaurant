from django.conf import settings

def login_redirect(request):
    url = request.META.get('HTTP_REFERER', settings.LOGIN_REDIRECT_URL)

    if 'next' in request.path:
        url = request.get_full_path()
    elif url.endswith(('login/', 'logout/')):
        url = settings.LOGIN_REDIRECT_URL
    
    return {'LOGIN_REDIRECT_URL': url}
