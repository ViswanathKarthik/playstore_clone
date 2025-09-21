from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup_view'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('search_suggestions/', views.search_suggestions, name='search_suggestions'),
    path('apps/', views.app_list, name='app_list'),
    path('app/<int:app_id>/', views.app_detail, name='app_detail'),
    path('app/<int:app_id>/all_reviews/', views.all_reviews, name='all_reviews'),
    path('app/<int:app_id>/submit_review/', views.submit_review, name='submit_review'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_review/<int:review_id>/', views.approve_review, name='approve_review'),
    path('search/', views.search_results, name='search_results'),
    path('admin/delete-review/<int:review_id>/', views.delete_review, name='delete_review'),


]
