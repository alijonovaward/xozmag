from django.shortcuts import redirect
from django.contrib.auth import logout


class ReadyCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                if not user.profile.ready:
                    logout(request)
                    return redirect('login')
            except AttributeError:
                pass  # Profil yo‘q bo‘lsa, hech narsa qilmaymiz

        response = self.get_response(request)
        return response
