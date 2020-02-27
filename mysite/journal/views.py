from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, DeleteView)
import random

from .models import Post
from .forms import PostForm
from .depression_detection_tweets import process_message, TweetClassifier, sc_tf_idf

class AboutView(TemplateView):
    template_name = 'about.html'

class HelpView(TemplateView):
    template_name = 'help.html'

def ActivityView(request):
    positive_counts = Post.objects.filter(neg_sentiment=False).count()
    negative_counts = Post.objects.filter(neg_sentiment=True).count()
    max_counts = positive_counts + negative_counts
    percentage = (negative_counts/max_counts)*100

    if percentage <= 25:
        activities = {
            'activity':['Take a bath','Something','else']
        }
    elif percentage > 25:
        activities = {
            'activity':['Do this','do that']
        }

    response = random.choice(activities.get('activity',[]))

    context = {
        'positive':positive_counts,
        'negative':negative_counts,
        'max':max_counts,
        'percentage':percentage,
        'test_activities':response
    }
    return render(request, 'journal/activities.html', context)

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