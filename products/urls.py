from django.urls import path, re_path

from products import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('product/<pk>', views.DetailProductView.as_view(), name='detail'),
    path('search/', views.searchPage, name='search'),

    path('searchresults/<str:category>/<str:maker>/<str:searchstring>/', views.SearchResultsView.as_view(),
         name='search_results'),



]
