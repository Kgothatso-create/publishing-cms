from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("all-articles", article_list, name="article list"),
    path("categories/", category_list, name="category list"),
    path("articles/new/", article_create, name="article-create"),
    path("articles/<slug:slug>/edit/", article_edit, name="article-edit"),
    path("<slug:slug>/", view_article, name="view article"),
    path("<slug:slug>/publish/", publish_article, name="publish article"),
    path("<slug:slug>/retract/", retract_article, name="retract article"),
    path("<slug:slug>/unpublish/", unpublish_article, name="unpublish article"),
    path("<slug:slug>/reject/", reject_article, name="reject article")
]
