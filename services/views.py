from django.shortcuts import render

# Create your views here.

def persian_office_services(request):
    return render(request, 'persian/persian_services/persian_office_services.html')

def persian_surgery_services(request):
    return render(request, 'persian/persian_services/persian_surgery_services.html')