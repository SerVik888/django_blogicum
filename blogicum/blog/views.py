from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from blog.constants import NUM_OF_POSTS
from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post, User


class PostListMixin(ListView):

    model = Post
    paginate_by = NUM_OF_POSTS
    template_name = 'blog/index.html'

    def get_queryset(self):
        self.select_posts = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        ).annotate(
            num_comments=Count('comments')
        ).order_by(
            '-pub_date'
        ).select_related(
            'author', 'category', 'location'
        )
        return self.select_posts


class PostCommentMixin:

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(reverse(
                'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
            ))
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostListView(PostListMixin):
    """Список постов на главной странице"""


class CategoryListView(PostListMixin):
    """Обрабатывает запрос на получение постов определённой категории."""

    template_name = 'blog/category.html'

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, is_published=True, slug=self.kwargs['post_category']
        )
        return super().get_queryset().filter(
            category__slug=self.kwargs['post_category']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileDetailView(PostListMixin):
    """Обрабатывает запрос на получение полного описания юзера
    со списком постов.
    """

    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.profile = get_object_or_404(
            User, username=self.kwargs['username']
        )

        if self.profile != self.request.user:
            queryset = super().get_queryset().filter(
                author__username=self.kwargs['username']
            )
        else:
            queryset = Post.objects.filter(
                author__username=self.kwargs['username']
            ).annotate(
                num_comments=Count('comments')
            ).order_by(
                '-pub_date'
            ).select_related(
                'author', 'category', 'location'
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class UserCreateView(CreateView):
    """Создание нового профиля"""

    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse('blog:index')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение профиля"""

    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    """Обрабатывает запрос на получение полного описания поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        if self.request.user.is_authenticated:
            return get_object_or_404(
                Post, Q(author=self.request.user)
                | (
                    Q(is_published=True)
                    & Q(category__is_published=True)
                    & Q(pub_date__lte=timezone.now())
                ),
                pk=self.kwargs['post_id']
            )
        return get_object_or_404(
            Post,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author', 'post')
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Обрабатывает запрос на Создание нового поста"""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )


class PostUpdateView(LoginRequiredMixin, PostCommentMixin, UpdateView):
    """Обрабатывает запрос на Редактирование поста"""

    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, PostCommentMixin, DeleteView):
    """Обрабатывает запрос на Удаление поста"""

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.object.author.username}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['form'].instance.post = get_object_or_404(
            Post, pk=self.kwargs['post_id']
        )
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):
    """Создание комментария."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post, pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateView(
    LoginRequiredMixin, CommentMixin, PostCommentMixin, UpdateView
):
    """Обновление коментария"""


class CommentDeleteView(
    LoginRequiredMixin, CommentMixin, PostCommentMixin, DeleteView
):
    """Удаление комментария"""
