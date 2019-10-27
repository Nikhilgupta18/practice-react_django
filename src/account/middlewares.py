from django.shortcuts import redirect


class CompleteProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        if request.path == "/account/" + request.user.username + '/complete-registration/':
            pass
        elif request.path == '/account/login/':
            pass
        elif request.user.is_anonymous:
            pass
        elif request.user.is_superuser:
            pass
        elif request.user.student.complete_profile:
            pass
        elif not request.user.student.complete_profile:
            return redirect('/account/' + request.user.username + '/complete-registration/')

        # Code to be executed for each request/response after
        # the view is called.

        return response
