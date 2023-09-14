import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Question(models.Model):
    """
    A class representing a question.

    Attributes:
        question_text (str): The text of the question.
        pub_date (DateTime): The date and time when the question was published.
        end_date (DateTime): The date and time when the question's voting
                             period ends (optional).
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('published date', default=timezone.now)
    end_date = models.DateTimeField('end published date', null=True,
                                    blank=True)

    def __str__(self):
        """
        Returns a string representation of the question.
        """
        return self.question_text

    def was_published_recently(self):
        """
        Checks if the question was published recently (within the last day).

        Returns:
            bool: True if the question was published recently, False otherwise.
        """
        now = timezone.now()
        return (now - datetime.timedelta(days=1)) <= self.pub_date <= now

    def is_published(self):
        """
        Checks if the question is currently published.

        Returns:
            bool: True if the question is published, False otherwise.
        """
        return timezone.now() >= self.pub_date

    def can_vote(self):
        """
        Checks if the question can be voted on based on its publishing
        and end dates.

        Returns:
            bool: True if the question can be voted on, False otherwise.
        """
        if self.end_date is None:
            return timezone.now() >= self.pub_date
        else:
            return self.end_date >= timezone.now() >= self.pub_date


class Choice(models.Model):
    """
    A class representing a choice for a question.

    Attributes:
        question (Question): The question to which this choice belongs.
        choice_text (str): The text of the choice.
        votes (int): The number of votes this choice has received.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """
        Returns a string representation of the choice.
        """
        return self.choice_text

    @property
    def votes(self):
        """Return the number of votes for this choice."""
        return self.vote_set.count()

class Vote(models.Model):
    """
    Record a choice for a question made by a user
    """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} voted for {self.choice.choice_text}"