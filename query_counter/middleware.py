from .decorators import queries_counter


class DjangoQueryCounterMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    @queries_counter
    def __call__(self, request):
        return self.get_response(request)
