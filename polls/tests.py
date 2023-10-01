import datetime

from django.contrib.messages import get_messages
from django.test import TestCase
from django.utils import timezone
from .models import Question, Choice, Vote
from django.urls import reverse
import django.test
from django.contrib.auth.models import User
from mysite import settings


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
        time = timezone.now() - datetime.timedelta(hours=23,
                                                   minutes=59, seconds=59)
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


def create_question(question_text, days, end):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    time_end = timezone.now() + datetime.timedelta(days=end)
    return Question.objects.create(question_text=question_text,
                                   pub_date=time, end_date=time_end)


class QuestionIndexViewIspublishTests(TestCase):
    def test_present_question(self):
        """
        Question with pub_date is now are display on index page.
        """
        question = create_question(question_text="Past question.",
                                   days=0, end=1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the index page.
        """
        question = create_question(question_text="Past question.",
                                   days=-30, end=1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.",
                                   days=-30, end=1)
        create_question(question_text="Future question.", days=30, end=31)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.",
                                    days=-30, end=1)
        question2 = create_question(question_text="Past question 2.",
                                    days=-5, end=1)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


def create_choice(question, choice_Text):
    """
    Create a choice with the given `choice_text` and vote's number
    """
    return Choice.objects.create(question=question, choice_text=choice_Text)


class QuestionCanVoteTests(TestCase):
    def test_cannot_vote_after_end_date(self):
        """
        Cannot vote if the end_date is in the past.
        """
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        question = create_question(question_text="Past question.",
                                   days=-2, end=-1)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('polls:vote', args=(question.id,)))
        self.assertContains(response, "The poll is not available.")

    def test_can_vote_present_question(self):
        """
        The detail view of a question with a pub_date at now
        displays the question's text.
        """
        question = create_question(question_text='Past Question.',
                                   days=0, end=1)
        response = self.client.get(reverse('polls:detail',
                                           args=(question.id,)))
        self.assertContains(response, question.question_text)

    def test_can_not_vote_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.',
                                          days=5, end=6)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse('polls:index'))

    def test_can_vote_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.',
                                        days=-5, end=1)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_can_vote_with_end_date_is_null_value(self):
        """
        the question with have no end date can be vote and show in index page
        """
        question = Question.objects.create(question_text="question_text",
                                           pub_date=timezone.now(), end_date=None)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question]
        )


class UserAuthTest(django.test.TestCase):
    def setUp(self):
        # superclass setUp creates a Client object and initializes test database
        super().setUp()
        self.username = "testuser"
        self.password = "FatChance!"
        self.user1 = User.objects.create_user(
            username=self.username,
            password=self.password,
            email="testuser@nowhere.com"
        )
        self.user1.first_name = "Tester"
        self.user1.save()
        # we need a poll question to test voting
        q = Question.objects.create(question_text="First Poll Question")
        q.save()
        # a few choices
        for n in range(1, 4):
            choice = Choice(choice_text=f"Choice {n}", question=q)
            choice.save()
        self.question = q

    def test_logout(self):
        """A user can logout using the logout url.

        As an authenticated user,
        when I visit /accounts/logout/
        then I am logged out
        and then redirected to the login page.
        """
        logout_url = reverse("logout")
        # Authenticate the user.
        # We want to logout this user, so we need to associate the
        # user user with a session.  Setting client.user = ... doesn't work.
        # Use Client.login(username, password) to do that.
        # Client.login returns true on success
        self.assertTrue(
            self.client.login(username=self.username, password=self.password)
        )
        # visit the logout page
        response = self.client.get(logout_url)
        self.assertEqual(302, response.status_code)

        # should redirect us to where? Polls index? Login?
        self.assertRedirects(response, reverse(settings.LOGOUT_REDIRECT_URL))

    def test_login_view(self):
        """A user can login using the login view."""
        login_url = reverse("login")
        # Can get the login page
        response = self.client.get(login_url)
        self.assertEqual(200, response.status_code)
        # Can login using a POST request
        # usage: client.post(url, {'key1":"value", "key2":"value"})
        form_data = {"username": "testuser",
                     "password": "FatChance!"
                     }
        response = self.client.post(login_url, form_data)
        # after successful login, should redirect browser somewhere
        self.assertEqual(302, response.status_code)
        # should redirect us to the polls index page ("polls:index")
        self.assertRedirects(response, reverse(settings.LOGIN_REDIRECT_URL))

    def test_auth_required_to_vote(self):
        """Authentication is required to submit a vote.

        As an unauthenticated user,
        when I submit a vote for a question,
        then I am redirected to the login page
          or I receive a 403 response (FORBIDDEN)
        """
        vote_url = reverse('polls:vote', args=[self.question.id])

        # what choice to vote for?
        choice = self.question.choice_set.first()
        # the polls detail page has a form, each choice is identified by its id
        form_data = {"choice": f"{choice.id}"}
        response = self.client.post(vote_url, form_data)
        # should be redirected to the login page
        self.assertEqual(response.status_code, 302)  # could be 303
        login_with_next = f"{reverse('login')}?next={vote_url}"
        self.assertRedirects(response, login_with_next)


class Vote_test(django.test.TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )
        self.question = create_question(
            question_text="Past question.",
            days=-2,
            end=5
        )
        self.choice = Choice.objects.create(
            question=self.question,
            choice_text="hello"
        )
        self.choice2 = Choice.objects.create(
            question=self.question,
            choice_text="hello1"
        )
        self.client.login(username='testuser', password='testpassword')

    def test_can_vote_only_one_time(self):
        """
        One user can vote only once.
        """
        # Simulate the user's first vote
        response = self.client.post(reverse('polls:vote',
                                            args=(self.question.id,)), {'choice': self.choice.id})
        self.assertRedirects(response, reverse('polls:results', args=(self.question.id,)))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().choice, self.choice)
        self.assertEqual(Vote.objects.get().user, self.user)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Your vote for {self.choice.choice_text} has been saved")

        # Attempt to vote again
        response = self.client.post(reverse('polls:vote',
                                            args=(self.question.id,)), {'choice': self.choice.id})
        self.assertEqual(Vote.objects.count(), 1)  # Vote count should not change

    def test_vote_change(self):
        """
        User can change the vote by delete the old one.
        """
        # Simulate the user's first vote
        response = self.client.post(reverse('polls:vote',
                                            args=(self.question.id,)), {'choice': self.choice.id})
        self.assertRedirects(response, reverse('polls:results', args=(self.question.id,)))
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().choice, self.choice)
        self.assertEqual(Vote.objects.get().user, self.user)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         f"Your vote for {self.choice.choice_text} has been saved")

        # Attempt to change the vote to another choice
        response = self.client.post(reverse('polls:vote',
                                            args=(self.question.id,)), {'choice': self.choice2.id})
        self.assertRedirects(response, reverse('polls:results', args=(self.question.id,)))
        self.assertEqual(Vote.objects.count(), 1)  # Vote count should remain the same

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         f"Change vote to {self.choice2.choice_text} has been saved")
