from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Department, Job
from .forms import DepartmentCreateForm, JobCreateForm


def job_list(request):

    jobs = Job.objects.select_related(
        "department"
    ).all()

    letter = request.GET.get("letter")

    if letter:
        jobs = jobs.filter(
            title__istartswith=letter
        )

    search = request.GET.get("q")

    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(department__name__icontains=search)
        )

    jobs = jobs.order_by("title")
    paginator = Paginator(jobs, 100)

    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)

    context = {
        "page_title": "Jobs",
        "create_url": "job-create",
        "create_label": "Add Job",
        "create_icon": "fas fa-briefcase",
        "search_placeholder": "Search jobs...",
        "list_url": "job-list",
        "items": jobs,
        "pagination_object": jobs,
        "icon": "fas fa-briefcase",
        "empty_message": "No jobs found.",
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "layouts/list_view.html",
        context
    )


def job_create(request):

    if request.method == "POST":
        form = JobCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job-list")
    else:
        form = JobCreateForm()

    return render(
        request,
        "job/add_job.html",
        {"form": form}
    )


def department_list(request):

    departments = Department.objects.all()

    letter = request.GET.get("letter")

    if letter:
        departments = departments.filter(
            name__istartswith=letter
        )

    search = request.GET.get("q")

    if search:
        departments = departments.filter(
            Q(name__icontains=search) |
            Q(code__icontains=search)
        )

    departments = departments.order_by("name")

    paginator = Paginator(departments, 100)

    page_number = request.GET.get("page")
    departments = paginator.get_page(page_number)

    context = {
        "page_title": "Departments",
        "create_url": "department-create",
        "create_label": "Add Department",
        "create_icon": "fas fa-building",
        "search_placeholder": "Search departments...",
        "list_url": "department-list",
        "items": departments,
        "pagination_object": departments,
        "icon": "fas fa-building",
        "empty_message": "No departments found.",
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "layouts/list_view.html",
        context
    )


def department_create(request):

    if request.method == "POST":
        form = DepartmentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("department-list")

    else:
        form = DepartmentCreateForm()

    return render(
        request,
        "job/add_department.html",
        {"form": form}
    )

