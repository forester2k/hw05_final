# posts/views.py
from django.contrib.auth.decorators import login_required
# from django.views.decorators.cache import cache_page
from django.shortcuts import redirect, render, get_object_or_404

from core.diffs import page_cuter
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


# @cache_page(20)
def index(request):
    post_list = Post.objects.all()
    context = {
        'page_obj': page_cuter(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
        'page_obj': page_cuter(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    following = False
    if user.is_authenticated:
        following = Follow.objects.filter(user=user, author=author).exists()
    post_list = author.posts.all()
    context = {
        'page_obj': page_cuter(request, post_list),
        'page_count': post_list.count(),
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comment_list = post.comments.all()
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.save()
        return redirect('posts:add_comment', post_id)
    context = {
        'post': post,
        'post_count': post.author.posts.count(),
        'comments': comment_list,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_list = request.user.follower.all()
    post_list = Post.objects.filter(author__in=follow_list.values('author'))
    context = {
        'page_obj': page_cuter(request, post_list),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    follower = request.user
    following = get_object_or_404(User, username=username)
    if follower != following:
        Follow.objects.get_or_create(
            user=follower,
            author=following
        )
    return redirect('posts:profile', username=following)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    follower = request.user
    following = get_object_or_404(User, username=username)
    to_delete = get_object_or_404(Follow, user=follower, author=following)
    to_delete.delete()
    return redirect('posts:profile', username=following)
