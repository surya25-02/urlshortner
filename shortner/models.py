from django.contrib.auth.models import User
from django.db import models 
from .utils import shortcode_generator

class Link(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    long_url = models.URLField(max_length=200, null=True)
    short_code = models.CharField(max_length=10, unique=True, blank=True)
    total_views = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_code 

    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = shortcode_generator()
        super(Link, self).save(*args, **kwargs)

class UserStatistics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    total_month_views = models.IntegerField(default=0)
    total_today_views = models.IntegerField(default=0)