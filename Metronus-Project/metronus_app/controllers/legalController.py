from django.shortcuts import render


def cookie_policy(request):
    return render(request, 'legal/cookie_policy.html')


def legal_terms(request):
    return render(request, 'legal/terms.html')