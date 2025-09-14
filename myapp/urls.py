from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start-from-zero/', views.start_from_zero, name='start_from_zero'),
    path('placement-test/', views.placement_test, name='placement_test'),
    path('learning-content/', views.learning_content, name='learning_content'),
    path('mark-term-studied/<int:term_id>/', views.mark_term_studied, name='mark_term_studied'),
    path('mark-rule-studied/<int:rule_id>/', views.mark_rule_studied, name='mark_rule_studied'),
    path('check-problem-answer/<int:problem_id>/', views.check_problem_answer, name='check_problem_answer'),
    path("search/", views.search, name="search"),

]