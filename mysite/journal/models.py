from django.db import models
from django.utils import timezone
from django.urls import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(max_length=280)
    created_date = models.DateTimeField(default=timezone.now)
    neg_sentiment = models.BooleanField(default=False)

    # Redirects the page after it is saved, this method is required when using CreateView
    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title