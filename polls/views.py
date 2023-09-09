from django.http import HttpResponseRedirect
from .models import Question, Choice
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic


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


def vote(request, question_id):
    """
    View for handling user votes on a question.
    """
    question = get_object_or_404(Question, pk=question_id)
    # Check if the user can vote on this question.
    if question.can_vote():
        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form with an error message.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            selected_choice.votes += 1
            selected_choice.save()
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    else:
        # User cannot vote on this question, so display an error message.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "The poll has already ended.",
        })
