from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from articles.models import ArticleReport
from job.models import Job
from .models import CompanyEvent, Employment, Role
from .forms import CompanyEventForm, EmployeeCreateForm, EmployeeEditForm, NotificationForm, RoleCreateForm


def employee_dashboard(request):

    company_events = CompanyEvent.objects.select_related(
        "created_by"
    ).order_by("-created_at")[:4]

    active_job_count = Job.objects.filter(is_active=True).distinct().count()
    active_employee_count = Employment.objects.filter(
        status=Employment.EmploymentStatus.ACTIVE
    ).distinct().count()

    reported_article_count = ArticleReport.objects.filter(
        resolved=False
    ).values(
        "article"
    ).distinct().count()

    context = {
        "reported_article_count": reported_article_count,
        "active_job_count": active_job_count,
        "active_employee_count": active_employee_count,
        "company_events": company_events,
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
        "list_url": "employee_list",
        "items": employees,
        "pagination_object": employees,
        "icon": "fas fa-user",
        "empty_message": "No employees found.",
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
        "detail_url_name": "employee_detail",
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
            return redirect("employee_list")
    else:
        form = EmployeeCreateForm()

    return render(
        request,
        "employment/add_employee.html",
        {"form": form}
    )


@login_required
def employee_detail(request, id):
    """
    Display an individual employee's details.

    Args:
        request: HTTP request.
        id: Employee employment UUID.

    Returns:
        Rendered employee detail page.
    """

    employee = get_object_or_404(
        Employment.objects.select_related(
            "user",
            "role",
            "job",
            "manager__user",
        ),
        id=id,
    )

    context = {
        "employee": employee,
    }

    return render(
        request,
        "employment/employee_details.html",
        context,
    )


@login_required
def employee_edit(request, id):
    """
    Edit an employee's user, employment and profile information.

    Args:
        request: HTTP request.
        id: Employee employment UUID.

    Returns:
        Rendered edit page or redirect to employee details.
    """

    employee = get_object_or_404(
        Employment.objects.select_related(
            "user",
            "role",
            "job",
            "manager__user",
            "profile",
        ),
        id=id,
    )

    if request.method == "POST":
        form = EmployeeEditForm(
            request.POST,
            employee=employee,
        )

        if form.is_valid():
            employee = form.save()

            messages.success(
                request,
                "Employee information updated successfully.",
            )

            return redirect(
                "employee_detail",
                id=employee.id,
            )

    else:
        form = EmployeeEditForm(employee=employee)

    context = {
        "employee": employee,
        "form": form,
        "page_title": "Edit Employee",
    }

    return render(
        request,
        "employment/employee_edit.html",
        context,
    )


@login_required
def employee_delete(request, id):
    """
    Delete an employee's employment record.

    Args:
        request: HTTP request.
        id: Employee employment UUID.

    Returns:
        Rendered confirmation page or redirect to employee list.
    """
    employee = get_object_or_404(
        Employment.objects.select_related(
            "user",
            "role",
            "job",
            "profile",
        ),
        id=id,
    )

    if request.method == "POST":
        employee.delete()

        messages.success(
            request,
            "Employee deleted successfully.",
        )

        return redirect("employee_list")

    context = {
        "employee": employee,
        "page_title": "Delete Employee",
    }

    return render(
        request,
        "employment/employee_delete.html",
        context,
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
        "detail_url_name": "role_detail",
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
        {"form": form},
    )


def role_detail(request, id):
    role = get_object_or_404(
        Role,
        id=id
    )

    context = {
        "role": role,
        "page_title": role.name,
    }

    return render(
        request,
        "employment/role_detail.html",
        context
    )



def calendar_view(request):
    events = CompanyEvent.objects.filter(
        event_date__gte=timezone.localdate() - timedelta(days=2)
    ).order_by("event_date")

    calendar_events = [
        {
            "title": event.title,
            "start": event.event_date.isoformat(),
            "allDay": True,
        }
        for event in events
    ]

    return render(request, "layouts/calendar.html", {
        "calendar_events": calendar_events,
    })


@login_required
def create_company_event(request):
    if request.method == "POST":
        form = CompanyEventForm(request.POST)

        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()

            messages.success(
                request,
                "Calendar event created successfully."
            )

            return redirect("calendar")
    else:
        form = CompanyEventForm()

    return render(
        request,
        "employment/create_event.html",
        {"form": form},
    )


@login_required
def company_events(request):
    events = CompanyEvent.objects.select_related(
        "created_by"
    ).order_by("-created_at")

    return render(
        request,
        "employment/all_events.html",
        {"events": events}
    )


@login_required
def company_event_detail(request, event_id):
    event = get_object_or_404(
        CompanyEvent.objects.select_related("created_by"),
        id=event_id,
    )

    return render(
        request,
        "employment/event_details.html",
        {"event": event}
    )


@login_required
def edit_company_event(request, event_id):
    event = get_object_or_404(
        CompanyEvent,
        id=event_id,
        created_by=request.user,
    )

    if request.method == "POST":
        form = CompanyEventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Company event updated successfully."
            )

            return redirect(
                "company_event_detail",
                event_id=event.id,
            )
    else:
        form = CompanyEventForm(instance=event)

    return render(
        request,
        "employment/edit_event.html",
        {
            "form": form,
            "event": event,
        },
    )


@login_required
def delete_company_event(request, event_id):
    event = get_object_or_404(
        CompanyEvent,
        id=event_id,
        created_by=request.user,
    )

    if request.method == "POST":
        event.delete()

        messages.success(
            request,
            "Company event deleted successfully."
        )

        return redirect("company_events")

    return render(
        request,
        "employment/delete_event.html",
        {
            "event": event,
        },
    )


@login_required
def create_notification(request):
    employee = get_object_or_404(
        Employment,
        user=request.user,
        status=Employment.EmploymentStatus.ACTIVE
    )

    if request.method == "POST":
        form = NotificationForm(request.POST)

        if form.is_valid():
            notification = form.save(commit=False)
            notification.created_by = employee
            notification.save()
            form.save_m2m()

            messages.success(request, "Notification created successfully.")
            return redirect("employee_dashboard")

    else:
        form = NotificationForm()

    return render(request, "employment/create_notification.html", {
        "form": form,
    })

