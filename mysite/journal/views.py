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
    if(max_counts != 0):
        percentage = (negative_counts/max_counts)*100
    else:
        percentage = 0
    

    if percentage == 100:
        activities_dict = {
            'activity':['Talk to a friend', 'Talk to a family member','Talk to someone','Take a look at our help page','Meditate']
        }   
    elif percentage < 50:
        activities_dict = {
            'activity':['Study','Do your chores','Take a swim','Go outside','Organize your space','Learn something new',
            'Play a video game','Listen to your favorite music','Read a book','Exercise']
        }
    else:
        activities_dict = {
            'activity':['Take a break','Get some rest','Take a stroll around your local park','Learn something new','Exercise',
            'Go out and get some fresh air','Meditate','Relax','Get a pet','Learn to garden','Volunteer for charity',
            'Read a book','Listen to music','Take a roadtrip','Take a long hot bath','Talk to a friend','Talk to someone',
            'Talk to a family member','Talk to a friend','Visit the help page','Play a video game','Play board games with friends',
            'Go to the beach','Take a swim','Discover new music']
        } 

    response = random.sample(list(activities_dict.get('activity')),5)

    context = {
        'positive':positive_counts,
        'negative':negative_counts,
        'max':max_counts,
        'percentage':percentage,
        'activities':response
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