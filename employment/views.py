from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q

from articles.models import ArticleReport
from job.models import Job
from .models import Employment, Role
from .forms import EmployeeCreateForm, RoleCreateForm


def employee_dashboard(request):

    active_job_count = Job.objects.filter(is_active=True).distinct().count()
    active_employee_count = Employment.objects.filter(status=True).distinct().count()

    reported_article_count = ArticleReport.objects.filter(
        resolved=False
    ).values(
        "article"
    ).distinct().count()

    context = {
        "reported_article_count": reported_article_count,
        "active_job_count": active_job_count,
        "active_employee_count": active_employee_count,
    }

    return render(request, "employment/dashboard.html", context)


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
        "page_title": "Employees",
        "create_url": "employee-create",
        "create_label": "Add Employee",
        "create_icon": "fas fa-user-plus",
        "search_placeholder": "Search employees...",
        "list_url": "employee-list",
        "items": employees,
        "pagination_object": employees,
        "icon": "fas fa-user",
        "empty_message": "No employees found.",
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "layouts/list_view.html",
        context
    )


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


def role_list(request):

    roles = Role.objects.all()
    letter = request.GET.get("letter")
    if letter:
        roles = roles.filter(
            name__istartswith=letter
        )

    search = request.GET.get("q")
    if search:
        roles = roles.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )

    roles = roles.order_by("name")
    paginator = Paginator(roles, 100)
    page_number = request.GET.get("page")
    roles = paginator.get_page(page_number)

    context = {
        "page_title": "Roles",
        "create_url": "role-create",
        "create_label": "Add Role",
        "create_icon": "fas fa-user-tag",
        "search_placeholder": "Search roles...",
        "list_url": "role-list",
        "items": roles,
        "pagination_object": roles,
        "icon": "fas fa-user-tag",
        "empty_message": "No roles found.",
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "layouts/list_view.html",
        context,
    )


def role_create(request):

    if request.method == "POST":
        form = RoleCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("role-list")

    else:
        form = RoleCreateForm()

    return render(
        request,
        "employment/add_role.html",
        {"form": form,},
    )
