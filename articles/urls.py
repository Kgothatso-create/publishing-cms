from django.urls import path
from .views import home, view_article, article_list

urlpatterns = [
    path("", home, name="home"),
    path("<slug:slug>/", view_article, name="view article"),
    path("all-articles", article_list, name="article list"),
]
