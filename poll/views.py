from django.http import HttpResponseRedirect
from .models import Question,Choice
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.utils import timezone

class IndexView(generic.ListView):
    template_name = 'poll/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        all_questions = Question.objects.all()
        # check if the question is published recently and can vote
        question = [q for q in all_questions if q.is_published() and q.can_vote() and q.was_published_recently()]
        # sort and select last 5 question
        question_index = sorted(question,key=lambda q: q.pub_date,reverse=True)[:5]
        return question_index

class DetailView(generic.DetailView):
    model = Question
    template_name = 'poll/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        all_questions = Question.objects.all()
        # check if the question is published recently and can vote
        question = [q for q in all_questions if q.is_published()]

        return Question.objects.filter(question_text__in=question)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'poll/results.html'



def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'poll/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('poll:results', args=(question.id,)))

