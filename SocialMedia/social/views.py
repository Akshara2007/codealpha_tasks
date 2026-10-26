
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Post, Like, Comment, Follow, Profile
@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.bio = request.POST.get("bio", "").strip()
        profile.profile_picture = request.POST.get("profile_picture", "").strip()
        profile.save()
        return redirect("profile", user_id=request.user.id)

    return render(request, "social/edit_profile.html", {
        "profile": profile
    })



def home(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "social/home.html", {"posts": posts})



@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Post.objects.create(user=request.user, content=content)
    return redirect("home")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please fill in all fields.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            login(request, user)
            return redirect("home")

    return render(request, "social/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(
            request, username=username, password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "social/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("home")


@login_required
def like_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(
            post=post, user=request.user
        )

        if not created:
            like.delete()

    return redirect("home")


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get("content", "").strip()

        if content:
            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

    return redirect("home")

@login_required
def follow_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)

        if target_user != request.user:
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=target_user
            )

            if not created:
                follow.delete()

    return redirect("home")

def profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(
        user=profile_user
    )
    posts = Post.objects.filter(
        user=profile_user
    ).order_by("-created_at")

    return render(request, "social/profile.html", {
        "profile_user": profile_user,
        "profile": profile,
        "posts": posts,
    })
