from django.http import HttpRequest, HttpResponse
from django.urls import path

from app.models import Parent


def index(_: HttpRequest) -> HttpResponse:
    lines = []
    for parent in Parent.objects.all():
        lines.append(f"<li>{parent}</li><ul>")
        for child in parent.children.all():
            lines.append(f"<li>{child}</li><ul>")
            for grandson in child.grandchildren.all():
                lines.append(f"<li>{grandson}</li>")
            lines.append("</ul>")
        lines.append("</ul>")
    return HttpResponse("".join(["<ul>", *lines, "</ul>"]))


urlpatterns = [path("", index)]
