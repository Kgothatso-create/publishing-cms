from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Employment


def employee_dashboard(request):
    return render(request, "employment/dashboard.html")


def employee_list(request):
    employees = Employment.objects.select_related("user").all()
    user = request.user

    # Department restriction
    if not user.is_superuser and not user.is_staff:

        if hasattr(user, "employment"):
            employees = employees.filter(department=user.employment.job.department)
        else:
            employees = employees.none()

    # Alphabet filter
    letter = request.GET.get("letter")

    if letter:
        employees = employees.filter(
            Q(user__first_name__istartswith=letter) |
            Q(user__last_name__istartswith=letter)
        )

    # Search
    search = request.GET.get("q")

    if search:
        employees = employees.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search)
        )

    employees = employees.order_by("user__first_name", "user__last_name")

    # Pagination
    paginator = Paginator(employees, 100)
    page_number = request.GET.get("page")
    employees = paginator.get_page(page_number)

    context = {
        "employees": employees,
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "employment/employees.html",
        context
    )


from django.shortcuts import redirect

from .forms import EmployeeCreateForm


def employee_create(request):

    if request.method == "POST":

        form = EmployeeCreateForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("employee-list")

    else:
        form = EmployeeCreateForm()

    return render(
        request,
        "employment/add_employee.html",
        {
            "form": form
        }
    )