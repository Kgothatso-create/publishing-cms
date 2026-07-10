from collections import OrderedDict

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from articles.forms import ArticleForm
from articles.models import Article, Category
from people.models import User


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


def article_list(request, category_slug=None, author_slug=None,):

    articles = Article.objects.select_related(
            "author", "category"
        ).filter(status="published").order_by("-published_at")

    category = None

    if author_slug:
        author = get_object_or_404(User, slug=author_slug)
        articles = articles.filter(author=author)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=category)

    paginator = Paginator(articles, 9)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "category": category,
        "author": author,
    }

    return render(
        request,
        "articles/list.html",
        context
    )


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


def category_list(request: HttpRequest):
    published_articles = (
        Article.objects.filter(status=Article.STATUS_PUBLISHED)
        .select_related("author", "category")
        .order_by("-published_at")
    )

    categories = (
        Category.objects.annotate(
            article_count=Count(
                "articles",
                filter=Q(articles__status=Article.STATUS_PUBLISHED),
            )
        )
        .filter(article_count__gt=0)
        .order_by("name")
        .prefetch_related(
            Prefetch(
                "articles",
                queryset=published_articles,
                to_attr="published_articles",
            )
        )
    )

    grouped_categories = OrderedDict()

    for category in categories:
        letter = category.name[0].upper()

        grouped_categories.setdefault(letter, []).append(
            {"category": category, "articles": category.published_articles[:4]}
        )

    context = {
        "grouped_categories": grouped_categories,
        "alphabet": grouped_categories.keys(),
        "category_count": categories.count(),
    }

    return render(
        request,
        "articles/category_list.html",
        context,
    )


def author_list(request):

    published_articles = Article.objects.filter(
            status=Article.STATUS_PUBLISHED
        ).select_related("author", "category").order_by("-published_at")

    authors = (
        User.objects
        .annotate(
            article_count=Count(
                "articles",
                filter=Q(
                    articles__status=Article.STATUS_PUBLISHED
                ),
            )
        )
        .filter(
            article_count__gt=0
        )
        .order_by(
            "first_name",
            "last_name"
        )
        .prefetch_related(
            Prefetch(
                "articles",
                queryset=published_articles,
                to_attr="published_articles",
            )
        )
    )

    grouped_authors = OrderedDict()

    for author in authors:
        name = author.get_full_name()
        if not name:
            name = author.username

        letter = name[0].upper()

        grouped_authors.setdefault(
            letter,
            []
        ).append(
            {"author": author, "articles": author.published_articles[:4]}
        )

    context = {
        "grouped_authors": grouped_authors,
        "alphabet": grouped_authors.keys(),
        "author_count": authors.count(),
    }

    return render(
        request,
        "articles/author_list.html",
        context,
    )
