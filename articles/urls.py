from django.urls import path
from .views import article_create, article_edit, home, view_article, article_list

urlpatterns = [
    path("", home, name="home"),
    path("<slug:slug>/", view_article, name="view article"),
    path("all-articles", article_list, name="article list"),
    path("articles/new/", article_create, name="article-create"),
    path("articles/<slug:slug>/edit/", article_edit, name="article-edit"),
]
