from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Project, Task


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "projects/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "projects/login.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")


@login_required
def dashboard(request):
    projects = Project.objects.filter(
        created_by=request.user
    ).prefetch_related("tasks").order_by("-created_at")

    for project in projects:
        total_tasks = project.tasks.count()
        completed_tasks = project.tasks.filter(
            status="completed"
        ).count()

        project.total_tasks_count = total_tasks
        project.completed_tasks_count = completed_tasks

        project.progress_percentage = (
            round((completed_tasks / total_tasks) * 100)
            if total_tasks > 0 else 0
        )

    return render(request, "projects/dashboard.html", {
        "projects": projects
    })
@login_required
def create_project(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()

        if title:
            Project.objects.create(
                title=title,
                description=description,
                created_by=request.user
            )
            return redirect("dashboard")

    return render(request, "projects/create_project.html")
@login_required
def create_task(request, project_id):
    project = Project.objects.filter(
        id=project_id,
        created_by=request.user
    ).first()

    if project is None:
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        assigned_to_id = request.POST.get("assigned_to")
        status = request.POST.get("status", "todo")
        due_date = request.POST.get("due_date") or None

        if title:
            assigned_user = User.objects.filter(
                id=assigned_to_id
            ).first() if assigned_to_id else None

            valid_statuses = ["todo", "in_progress", "completed"]
            if status not in valid_statuses:
                status = "todo"

            Task.objects.create(
                project=project,
                title=title,
                description=description,
                assigned_to=assigned_user,
                status=status,
                due_date=due_date
            )
            return redirect("dashboard")

    return render(request, "projects/create_task.html", {
        "project": project,
        "users": User.objects.all()
    })
@login_required
def edit_task(request, task_id):
    task = Task.objects.filter(
        id=task_id,
        project__created_by=request.user
    ).first()

    if task is None:
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        assigned_to_id = request.POST.get("assigned_to")
        status = request.POST.get("status", "todo")
        due_date = request.POST.get("due_date") or None

        valid_statuses = ["todo", "in_progress", "completed"]

        if title and status in valid_statuses:
            task.title = title
            task.description = description
            task.assigned_to = (
                User.objects.filter(id=assigned_to_id).first()
                if assigned_to_id else None
            )
            task.status = status
            task.due_date = due_date
            task.save()

            return redirect("dashboard")

    return render(request, "projects/edit_task.html", {
        "task": task,
        "users": User.objects.all()
    })


@login_required
def delete_task(request, task_id):
    task = Task.objects.filter(
        id=task_id,
        project__created_by=request.user
    ).first()

    if task is None:
        return redirect("dashboard")

    if request.method == "POST":
        task.delete()
        return redirect("dashboard")

    return render(request, "projects/delete_task.html", {
        "task": task
    })