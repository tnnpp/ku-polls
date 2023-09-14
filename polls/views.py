from django.http import HttpResponseRedirect
from .models import Question, Choice, Vote
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

class IndexView(generic.ListView):
    """
    View for displaying a list of the latest published questions.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        all_questions = Question.objects.all()
        # Check if the question is published recently and can be voted on.
        question = [q for q in all_questions if q.is_published() and q.can_vote()]
        # Sort and select the last 5 questions.
        return Question.objects.filter(question_text__in=question).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    """
    View for displaying details of a question.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        all_questions = Question.objects.all()
        # Check if the question is published recently.
        question = [q for q in all_questions if q.is_published()]

        return Question.objects.filter(question_text__in=question)


class ResultsView(generic.DetailView):
    """
    View for displaying the results of a question.
    """
    model = Question
    template_name = 'polls/results.html'

@login_required
def vote(request, question_id):
    """
    View for handling user votes on a question.
    """
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    print("current user is", user.id, "login", user.username)
    print("Real name:", user.first_name, user.last_name)

    if not question.can_vote():
        # User cannot vote on this question, so display an error message.
        messages.error(request, "The polls is not available.")
        return render(request, 'polls/detail.html')

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        messages.error(request, "You didn't select a choice.")
        return render(request, "polls/detail.html", {'question': question})
    else:
        # check if user already voted.
        is_exist = Vote.objects.filter(choice__question=selected_choice.question, user=user).exists()
        if is_exist:
            messages.error(request, "You have already voted.")
            return render(request, "polls/detail.html", {'question': question})
        else:
            # create new vote object.
            vote = Vote(choice=selected_choice,user=user)
            vote.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))




