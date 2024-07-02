from django.urls import path

from products import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('product/<pk>', views.DetailProductView.as_view(), name='detail'),
    path('search/', views.searchPage, name='search'),
    path('searchresults/<str:category>/<str:maker>/<str:searchstring>/', views.SearchResultsView.as_view(),
         name='search_results'),
    path('product/productslist/', views.ProductListView.as_view(), name='product_list'),
    path('product/discountedproducts/', views.ProductListView.as_view(), name='product_discounted'),
    path('product/mostsoldproducts/', views.ProductListView.as_view(), name='product_mostsold'),

    path('staff/list/<str:type>', views.TableList.as_view(), name='staff_list'),


    path('staff/remove/country/<int:pk>/', views.RemoveCountry.as_view(), name='remove_country'),
    path('staff/maker/remove/<int:pk>/', views.RemoveMaker.as_view(), name='remove_maker'),
    path('staff/product/remove/<int:pk>/', views.RemoveProduct.as_view(), name='remove_product'),
    path('staff/model/remove/<int:pk>/', views.RemoveModel.as_view(), name='remove_model'),


    path('staff/country/add/', views.AddCountry.as_view(), name='add_country'),
    path('staff/maker/add/', views.AddMaker.as_view(), name='add_maker'),
    path('staff/product/add/', views.AddProduct.as_view(), name='add_product'),
    path('staff/model/add/', views.AddModel.as_view(), name='add_model'),

    path('staff/product/modify/<int:pk>/', views.ModifyProduct.as_view(), name='modify_product'),
    path('staff/model/modify/<int:pk>/', views.ModifyModel.as_view(), name='modify_model'),

]
