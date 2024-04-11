from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import Link, UserStatistics
from .serializers import LinkSerializer
from .utils import shortcode_generator


class HomeView(View):
    template_name = "shortner/home.html"

    def get(self, request):
        return render(request, self.template_name)


class UserLogout(View):
    def get(self, request):
        logout(request)
        return redirect("home")


class UserLogin(View):
    template_name = "shortner/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        if user := authenticate(username=username, password=password):
            login(request, user)
            return redirect("home")
        else:
            return render(
                request,
                self.template_name,
                {"error": True, "username": username, "password": password},
            )


class UserSignup(View):
    template_name = "shortner/signup.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        if authenticate(username=username, password=password):
            return render(
                request,
                self.template_name,
                {"error": True, "text": "You Already Have an Account, Please Login."},
            )
        elif User.objects.filter(username=username).exists():
            return render(
                request,
                self.template_name,
                {"error": True, "text": "Username is already taken."},
            )
        elif User.objects.filter(email=email).exists():
            return render(
                request,
                self.template_name,
                {"error": True, "text": "Email is already taken."},
            )

        user = User.objects.create_user(
            username=username, password=password, email=email
        )
        UserStatistics.objects.create(user=user)
        Token.objects.get_or_create(user=user)
        login(request, user)

        return redirect("home")


class GetShortLink(View):
    template_name = "shortner/404.html"

    def get(self, request, short_code=None):
        if not short_code:
            return render(request, self.template_name, status=404)

        link = Link.objects.filter(short_code=short_code)

        if link.exists():
            link = link.get()
            link.total_views += 1
            link.save()
            statistics = UserStatistics.objects.get(user=link.user)
            statistics.total_month_views += 1
            statistics.total_today_views += 1
            statistics.save()

            return redirect(link.long_url)


class DashboardView(LoginRequiredMixin, ListView):
    model = Link
    template_name = "shortner/dashboard.html"
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).order_by(
            "-created_date"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        statistics = UserStatistics.objects.get(user=self.request.user)
        context["Statistics"] = statistics
        return context


class URLShortenerAPI(APIView):
    model = Link
    parser_classes = [JSONParser, MultiPartParser]
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    @extend_schema(
        summary="Short Link",
        description="Create Link",
        request=LinkSerializer,
        responses={
            200: OpenApiResponse(description="Json Response"),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = LinkSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        long_url = serializer.validated_data.get("long_url")
        link, created = Link.objects.get_or_create(
            long_url=long_url,
            user=request.user,
            defaults={"short_code": shortcode_generator()},
        )

        return Response(
            {"shorten_link": f"https://{ request.get_host() }/{link.short_code}"},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Delete Link",
        description="Delete Link",
        request=LinkSerializer,
        parameters=[
            OpenApiParameter(
                name="url",
                description="Enter Shorten Url",
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            204: OpenApiResponse(description="No Content"),
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Not Found"),
        },
    )
    def delete(self, request):
        short_code = request.GET.get("url").split("/")[-1]
        link = get_object_or_404(self.model, short_code=short_code, user=request.user)
        link.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
