import datetime
from django.db import models
from django.utils import timezone
from django import forms
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField('end published date')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return (now - datetime.timedelta(days=1)) <= self.pub_date <= now

    def is_published(self):
        return timezone.now() > self.pub_date

    def can_vote(self):
        return self.end_date > timezone.now() > self.pub_date

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return  self.choice_text
