from django.shortcuts import render
from .models import ServiceItem
from team.models import TeamMember
from siteimages.models import DoctorPhoto


def _team():
    return TeamMember.objects.filter(is_active=True)


def persian_services_overview(request):
    return render(request, 'persian/persian_services/persian_services_overview.html', {
        'team_members': _team(),
    })


def persian_office_services(request):
    return render(request, 'persian/persian_services/persian_office_services.html', {
        'items': ServiceItem.objects.filter(type='office', is_active=True),
    })


def persian_surgery_services(request):
    return render(request, 'persian/persian_services/persian_surgery_services.html', {
        'items': ServiceItem.objects.filter(type='surgery', is_active=True),
        'doctor_photo_surgery': DoctorPhoto.objects.filter(type='surgery', is_active=True).first(),
    })


def english_services_overview(request):
    return render(request, 'english/english_services/english_services_overview.html', {
        'team_members': _team(),
    })


def english_office_services(request):
    return render(request, 'english/english_services/english_office_services.html', {
        'items': ServiceItem.objects.filter(type='office', is_active=True),
    })


def english_surgery_services(request):
    return render(request, 'english/english_services/english_surgery_services.html', {
        'items': ServiceItem.objects.filter(type='surgery', is_active=True),
        'doctor_photo_surgery': DoctorPhoto.objects.filter(type='surgery', is_active=True).first(),
    })


def arabic_services_overview(request):
    return render(request, 'arabic/arabic_services/arabic_services_overview.html', {
        'team_members': _team(),
    })


def arabic_office_services(request):
    return render(request, 'arabic/arabic_services/arabic_office_services.html', {
        'items': ServiceItem.objects.filter(type='office', is_active=True),
    })


def arabic_surgery_services(request):
    return render(request, 'arabic/arabic_services/arabic_surgery_services.html', {
        'items': ServiceItem.objects.filter(type='surgery', is_active=True),
        'doctor_photo_surgery': DoctorPhoto.objects.filter(type='surgery', is_active=True).first(),
    })
