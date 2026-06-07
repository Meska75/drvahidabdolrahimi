from django.shortcuts import render


def persian_services_overview(request):
    return render(request, 'persian/persian_services/persian_services_overview.html')


def persian_office_services(request):
    return render(request, 'persian/persian_services/persian_office_services.html')


def persian_surgery_services(request):
    return render(request, 'persian/persian_services/persian_surgery_services.html')


def english_services_overview(request):
    return render(request, 'english/english_services/english_services_overview.html')


def english_office_services(request):
    return render(request, 'english/english_services/english_office_services.html')


def english_surgery_services(request):
    return render(request, 'english/english_services/english_surgery_services.html')