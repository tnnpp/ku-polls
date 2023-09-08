import datetime
from django.test import TestCase
from django.utils import timezone
from .models import Question,Choice
from django.urls import reverse


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

def create_question(question_text, days,end):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    time_end = timezone.now() + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text, pub_date=time,end_date= time_end)

class QuestionIndexViewIspublishTests(TestCase):
    def test_present_question(self):
        """
        Question with pub_date is now are display on index page.
        """
        question = create_question(question_text="Past question.", days=0, end=1)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.", days=-30, end=1 )
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )


    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30,end=1)
        future_question = create_question(question_text="Future question.", days=30,end=31)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30,end=1)
        question2 = create_question(question_text="Past question 2.", days=-5,end=1)
        response = self.client.get(reverse('poll:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )
def create_choice(question,choice_Text,votes):
    """
    Create a choice with the given `choice_text` and vote's number
    """
    return Choice.objects.create(question=question, choice_text=choice_Text, votes=votes)

class QuestionCanVoteTests(TestCase):
    def test_cannot_vote_after_end_date(self):
        """
        Cannot vote if the end_date is in the past.
        """
        question = create_question(question_text="Past question.", days=-2, end=-1)
        vote = create_choice(question=question,choice_Text='a',votes=0)
        response = self.client.get(reverse('poll:vote', args=(question.id,)))
        self.assertContains(response, "The poll already ended.")

    def test_can_vote_present_question(self):
        """
        The detail view of a question with a pub_date at now
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=0, end=1)
        url = reverse('poll:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_can_not_vote_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5,end=6)
        url = reverse('poll:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_can_vote_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5,end=1)
        url = reverse('poll:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

