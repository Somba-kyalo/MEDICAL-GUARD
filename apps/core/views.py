from django.shortcuts import render


def home(request):
    return render(request, 'core/home.html')


def about(request):
    return render(request, 'core/about.html')


def dashboard(request):
    return render(request, 'core/dashboard.html')


def error_page(request):
    return render(request, 'core/error.html')