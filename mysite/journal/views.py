from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, DeleteView)

from .models import Post
from .forms import PostForm
from .depression_detection_tweets import process_message, TweetClassifier, sc_tf_idf

class AboutView(TemplateView):
    template_name = 'about.html'

class HelpView(TemplateView):
    template_name = 'help.html'

class PostListView(ListView):
    context_object_name = 'post_list'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(created_date__lte=timezone.now()).order_by('-created_date')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(CreateView):
    form_class = PostForm
    model = Post

    def form_valid(self, form):
        post = form.save(commit=False)
        pm = process_message(post.text)
        if sc_tf_idf.classify(pm):
            post.neg_sentiment = True
            post.save()
            return super(PostCreateView, self).form_valid(form)
        else:
            post.save()
            return super(PostCreateView, self).form_valid(form)

class PostDeleteView(DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')