from django.utils.timezone import now

from posts.models import User


def last_activity_middleware(get_response):
    """
    Updates user last activity on every request
    """
    def middleware(request):
        response = get_response(request)
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(last_activity=now())
        return response

    return middleware
