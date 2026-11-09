from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
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
        "list_url": "job_list",
        "items": jobs,
        "pagination_object": jobs,
        "icon": "fas fa-briefcase",
        "empty_message": "No jobs found.",
        "letters": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "selected_letter": letter,
        "search": search,
        "detail_url_name": "job_detail",
    }

    return render(
        request,
        "layouts/list_view.html",
        context,
    )


def job_detail(request, id):
    job = get_object_or_404(
        Job.objects.select_related("department"),
        id=id
    )

    context = {
        "job": job,
        "page_title": job.title,
    }

    return render(
        request,
        "job/job_details.html",
        context
    )


def job_create(request):

    if request.method == "POST":
        form = JobCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("job_list")
    else:
        form = JobCreateForm()

    return render(
        request,
        "job/add_job.html",
        {"form": form}
    )


@login_required
def job_edit(request, id):
    """
    Edit an existing job definition.

    Args:
        request: HTTP request.
        id: UUID of the job.

    Returns:
        Rendered job edit page or redirect after successful update.
    """
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job.job_code = request.POST.get("job_code", "").strip()
        job.title = request.POST.get("title", "").strip()
        job.description = request.POST.get("description", "").strip() or None
        job.department_id = request.POST.get("department")
        job.is_active = request.POST.get("is_active") == "on"
        job.level = request.POST.get("level") or None
        job.grade = request.POST.get("grade") or None

        job.save()

        messages.success(request, "Job updated successfully.")

        return redirect("job_detail", id=job.id)

    context = {
        "job": job,
        "departments": Department.objects.all(),
        "page_title": f"Edit {job.title}",
    }

    return render(
        request,
        "job/job_edit.html",
        context
    )


@login_required
def job_delete(request, id):
    """
    Delete an existing job definition.

    Args:
        request: HTTP request.
        id: UUID of the job.

    Returns:
        Rendered confirmation page or redirect after deletion.
    """
    job = get_object_or_404(Job, id=id)

    if request.method == "POST":
        job_title = job.title
        job.delete()

        messages.success(
            request,
            f"Job '{job_title}' deleted successfully."
        )

        return redirect("job_list")

    context = {
        "job": job,
        "page_title": f"Delete {job.title}",
    }

    return render(
        request,
        "job/job_delete.html",
        context
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
        "detail_url_name": "department_detail",
    }

    return render(
        request,
        "layouts/list_view.html",
        context
    )


def department_detail(request, id):
    department = get_object_or_404(Department, id=id)

    context = {
        "department": department,
        "page_title": department.name,
    }

    return render(
        request,
        "job/department_detail.html",
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

