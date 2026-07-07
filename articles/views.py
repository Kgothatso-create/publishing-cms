from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
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


def view_article(request, slug):
    articles = Article.objects.filter(status="published")

    article = get_object_or_404(
        Article.objects.select_related("author"),
        slug=slug,
        status="published",
    )

    related_articles = (
        Article.objects.filter(
            category=article.category,
            status="published",
        )
        .exclude(id=article.id)
        .order_by("-published_at")[:3]
    )

    context = {
        "article": article,
        "oldest_articles": articles.order_by("created_at"),
        "related_articles": related_articles,
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
            return redirect("article list")
    else:
        form = ArticleForm(instance=article)

    return render(request, "articles/article_form.html", {
        "form": form,
        "object": article
    })
