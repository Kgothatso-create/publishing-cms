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
        "jobs": jobs,
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "job/jobs.html",
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
        "departments": departments,
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
    }

    return render(
        request,
        "job/departments.html",
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

