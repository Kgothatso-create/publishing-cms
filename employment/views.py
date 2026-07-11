from django.shortcuts import render


def employee_dashboard(request):
    return render(request, "employment/dashboard.html")
