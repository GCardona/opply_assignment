from django.views.generic import TemplateView
from rest_framework.authentication import BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class HomeView(TemplateView):
    template_name = "home.html"


@api_view(["get"])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def token(request):
    return Response({"token": Token.objects.get_or_create(user=request.user)[0].key})
