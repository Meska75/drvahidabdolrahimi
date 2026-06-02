from django.shortcuts import render


def persian_home(request):
    return render(request, 'persian/persian_main/persian_home.html')


def persian_about(request):
    return render(request, 'persian/persian_main/persian_about.html')


def persian_contact(request):
    return render(request, 'persian/persian_main/persian_contact.html')
