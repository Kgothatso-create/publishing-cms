from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from articles.forms import ArticleForm
from articles.models import Article


def home(request):
    articles = Article.objects.filter(status="published")

    context = {
        "latest_articles": articles.order_by("-created_at"),  # main content
        "oldest_articles": articles.order_by("created_at"),   # sidebar
    }

    return render(request, "articles/home.html", context)


def view_article(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Display a single article.

    Published articles are publicly accessible. Draft articles are only
    accessible by their author, allowing authors to preview their own
    unpublished content.

    Determines whether the current user has permission to edit the article
    and passes this permission state to the template.

    Args:
        request (HttpRequest): The HTTP request object containing user
            authentication information.
        slug (str): The unique slug identifying the article.

    Returns:
        HttpResponse: Rendered article detail page containing the article,
            related articles, and edit permissions.
    """

    if request.user.is_authenticated:
        article = get_object_or_404(
            Article.objects.filter(
                Q(status=Article.STATUS_PUBLISHED)
                | Q(author=request.user)
            ),
            slug=slug,
        )
    else:
        article = get_object_or_404(
            Article,
            slug=slug,
            status=Article.STATUS_PUBLISHED,
        )

    related_articles = None

    if article.status == Article.STATUS_PUBLISHED:
        related_articles = (
            Article.objects.filter(
                category=article.category,
                status=Article.STATUS_PUBLISHED,
            )
            .exclude(id=article.id)
            .order_by("-published_at")[:3]
        )

    can_edit = (
        request.user.is_authenticated
        and article.author == request.user
    )

    can_moderate = (
            request.user.is_authenticated
            and request.user.is_staff
    )

    context = {
        "article": article,
        "related_articles": related_articles,
        "can_edit": can_edit,
        "can_moderate": can_moderate,
    }

    return render(request, "articles/view.html", context)


def article_list(request):
    articles = (
        Article.objects.select_related(
            "author",
            "category",
        )
        .filter(status="published")
        .order_by("-published_at")
    )

    paginator = Paginator(articles, 9)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(request, "articles/list.html", context)


@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.slug = slugify(article.title)
            article.status = Article.STATUS_DRAFT
            article.is_featured = False
            article.save()

            return redirect("view article", slug=article.slug)
    else:
        form = ArticleForm()

    return render(request, "articles/article_form.html", {
        "form": form,
        "object": None
    })


@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug, author=request.user)

    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)

        if form.is_valid():
            form.save()
            return redirect("view article", slug=article.slug)
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/article_form.html", {
        "form": form,
        "object": article
    })


@login_required
def publish_article(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Publish an article owned by the authenticated user.

    Changes the article status from draft to published and records the
    publication timestamp using the Article model publish method.

    Args:
        request (HttpRequest): The HTTP request containing the authenticated user.
        slug (str): The unique slug identifying the article.

    Returns:
        HttpResponse: Redirects the user back to the published article.
    """

    article = get_object_or_404(
        Article,
        slug=slug,
        author=request.user,
    )

    article.publish()

    return redirect("view article", slug=article.slug)


@login_required
def retract_article(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Retract an article owned by the authenticated user.

    Changes the article status from published to retracted.

    Args:
        request (HttpRequest): The HTTP request containing the authenticated user.
        slug (str): The unique slug identifying the article.

    Returns:
        HttpResponse: Redirects the user back to the article page.
    """

    article = get_object_or_404(
        Article,
        slug=slug,
        author=request.user,
    )

    article.retract()

    return redirect("view article", slug=article.slug)


@login_required
def unpublish_article(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Move an article from published back into draft status.

    Only the article owner can unpublish their article.

    Args:
        request (HttpRequest): The HTTP request containing the authenticated user.
        slug (str): The unique slug identifying the article.

    Returns:
        HttpResponse: Redirects the user back to the article page.
    """

    article = get_object_or_404(
        Article,
        slug=slug,
        author=request.user,
    )

    article.unpublish()

    return redirect("view article", slug=article.slug)


@staff_member_required
def reject_article(request: HttpRequest, slug: str) -> HttpResponse:
    """
    Reject an article through administrative moderation.

    Only Django staff users can reject articles.

    Args:
        request (HttpRequest): The HTTP request containing the authenticated staff user.
        slug (str): The unique slug identifying the article.

    Returns:
        HttpResponse: Redirects the admin back to the article page.
    """

    article = get_object_or_404(
        Article,
        slug=slug,
    )

    article.reject()

    return redirect("view article", slug=article.slug)