from django.urls import path, include
from .views import *


urlpatterns = [
    path("", home, name="home"),
    path("articles/", include([
        path("", article_list, name="article list"),
        path("new/", article_create, name="article-create"),
        path("author-list/", author_article_list, name="author articles"),
        path("<slug:slug>/", include([
            path("", view_article, name="view article"),
            path("edit/", article_edit, name="article-edit"),
            path("publish/", publish_article, name="publish article"),
            path("retract/", retract_article, name="retract article"),
            path("unpublish/", unpublish_article, name="unpublish article"),
            path("reject/", reject_article, name="reject article"),
        ])),
    ])),
    path("categories/", include([
        path("", category_list, name="category list"),
        path("<slug:category_slug>/", article_list, name="category articles"),
    ])),
    path("authors/", include([
        path("", author_list, name="author list"),
        path("<slug:author_slug>/", article_list, name="author articles"),
    ])),
    path("terms/", include([
        path("terms/", terms_view, name="terms"),
        path("privacy-policy/", privacy_policy_view, name="privacy_policy"),
    ]))
]
