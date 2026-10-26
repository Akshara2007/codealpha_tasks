from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("create-project/", views.create_project, name="create_project"),
    path(
        "project/<int:project_id>/create-task/",
        views.create_task,
        name="create_task"
    ),

    path(
        "task/<int:task_id>/edit/",
        views.edit_task,
        name="edit_task"
    ),
    path(
        "task/<int:task_id>/delete/",
        views.delete_task,
        name="delete_task"
    ),
]