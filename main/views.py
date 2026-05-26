from django.shortcuts import render

# Create your views here.

def persian_home(request):
    return render(request, 'persian_main/persian_home.html')

def persian_office_services(request):
    return render(request, 'persian_main/persian_office_services.html')

def persian_surgery_services(request):
    return render(request, 'persian_main/persian_surgery_services.html')

def persian_hperisian_contact(request):
    return render(request, 'persian_main/perisian_contact.html')

def persian_about(request):
    return render(request, 'persian_main/persian_about.html')