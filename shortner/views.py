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
        return redirect('home')


class UserLogin(View):
    template_name = "shortner/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if user := authenticate(username=username, password=password):
            login(request, user)
            return redirect("home")
        else:
            return render(request, self.template_name, {"error": True, "username": username, "password": password})


class UserSignup(View):
    template_name = 'shortner/signup.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if authenticate(username=username, password=password):
            return render(request, self.template_name, {'error': True, 'text': 'You Already Have an Account, Please Login.'})
        elif User.objects.filter(username=username).exists():
            return render(request, self.template_name, {'error': True, 'text': 'Username is already taken.'})
        elif User.objects.filter(email=email).exists():
            return render(request, self.template_name, {'error': True, 'text': 'Email is already taken.'})

        user = User.objects.create_user(
            username=username, password=password, email=email)
        login(request, user)
        Token.objects.get_or_create(user=user)
        return redirect('home')


class GetShortLink(View):
    template_name = "shortner/404.html"

    def get(self, request, short_code=None):
        if short_code and Link.objects.filter(short_code=short_code).exists():
            ob = Link.objects.get(short_code=short_code)
            ob.total_views += 1
            ob.save()
            Statistics, created = UserStatistics.objects.get_or_create(
                user=request.user)
            Statistics.total_month_views += 1
            Statistics.total_today_views += 1
            Statistics.save()
            return redirect(ob.long_url)
        else:
            return render(request, self.template_name, status=404)


class DashboardView(LoginRequiredMixin, ListView):
    model = Link
    template_name = 'shortner/dashboard.html'
    paginate_by = 10

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user).order_by('-created_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        Statistics, created = UserStatistics.objects.get_or_create(
            user=self.request.user)
        context['Statistics'] = Statistics
        return context


class URLShortenerAPI(APIView):
    model = Link
    parser_classes = [JSONParser, MultiPartParser]
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Short Link',
        description="Create Link",
        request=LinkSerializer,
        responses={
            200: OpenApiResponse(description='Json Response'),
            400: OpenApiResponse(description='Validation error')
        }
    )
    def post(self, request):
        data = request.data
        serializer = LinkSerializer(data=data)
        if serializer.is_valid():
            long_url = serializer.validated_data.get('long_url')
            short_code = shortcode_generator()
            Link.objects.create(long_url=long_url,
                            short_code=short_code, user=request.user)
            return Response({'shorten_link': f'https://{ request.get_host() }/{short_code}'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Delete Link',
        description="Delete Link",
        request=LinkSerializer,
        parameters=[
            OpenApiParameter(
                name='url',
                description='Enter Shorten Url',
                type=str,
                location=OpenApiParameter.QUERY
            ),
        ],
        responses={
            204: OpenApiResponse(description='No Content'),
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Not Found')
        }
    )
    def delete(self, request):
        short_code = request.GET.get('url').split('/')[-1]
        ob = get_object_or_404(self.model, short_code=short_code)
        ob.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
