from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Job
from .forms import JobCreateForm


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
