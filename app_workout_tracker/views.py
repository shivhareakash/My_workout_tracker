from django.shortcuts import render
from .models import Topic, Progress, Goal, Mistake
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from .forms import TopicForm, GoalForm, MistakeForm, ProgressForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404

# Create your views here.

## Public Views ###
def public_topics_list(request):
    '''List view of all public topics'''
    public_topics = Topic.objects.filter(view_option=True)
    # .order_by('-date_added') is not neeeded here as we already set the default ordering in Models
    context = {'public_topics':public_topics}
    return render(request, 'workout_tracker/home.html', context)

def public_subtopic_list(request, topic_id, subtopic_name):
    '''Goal list of one of the public topics with topic_id
    This function takes topic_id and subtopic_name as arguments and render the appropriate subtopic accordingly'''

    public_topic = get_object_or_404(Topic.objects.filter(view_option=True), id=topic_id)

## More coding but efficient way to save queries:
    if subtopic_name=='goals_list':
        context = {'called_submodel': public_topic.goal_set.all(), 'subtopic_name': subtopic_name}

    elif subtopic_name=='progress_list':
        context = {'called_submodel': public_topic.progress_set.all(), 'subtopic_name': subtopic_name}

    elif subtopic_name=='mistakes_list':
        context= {'called_submodel': public_topic.mistake_set.all(), 'subtopic_name' :subtopic_name}


    return render(request,'workout_tracker/entry_list.html', context)


def public_subtopic_detail(request, subtopic_id, subtopic_name):
    public_goal_list = Goal.objects.filter(topic__view_option=True)
    public_mistake_list = Mistake.objects.filter(topic__view_option=True)
    public_progress_list = Progress.objects.filter(topic__view_option=True)

    #churning_subtopic_name i.e from goals_list to goals
    churned_subtopic_name = subtopic_name.split(subtopic_name[-5:])[0]

    if churned_subtopic_name== 'goals':
        detail = get_object_or_404(public_goal_list, id=subtopic_id)
    elif churned_subtopic_name == 'mistakes':
        detail = get_object_or_404(public_mistake_list, id=subtopic_id)
    elif churned_subtopic_name== 'progress':
       detail = get_object_or_404(public_progress_list, id=subtopic_id)

    context = {'detail':detail, 'subtopic_name':subtopic_name}
    return render(request, 'workout_tracker/entry_detail.html', context)

#
## Secure Views ###
## We are going to use Django's generic view heere instead of the legthy programming we did above for public view

class secure_topics_list(LoginRequiredMixin, generic.ListView):
    '''This is a list view class restricted to registered user, returns the topic list created by the user'''

    template_name = 'workout_tracker/secure_home.html'
    context_object_name = 'user_topics'

    def get_queryset(self):
        user_topics = Topic.objects.filter(owner=self.request.user).order_by('-date_added')
        return user_topics


class secure_subtopic_list(LoginRequiredMixin, generic.ListView):
    '''This is a list view class restricted to registered user, returns the user's subtopic list based
    on the subtopic_name and topic_id passed from the home page'''

    template_name = 'workout_tracker/secure_entry_list.html'
    context_object_name = 'called_submodel'

    def get_queryset(self, **kwargs):
        subtopic_name = self.kwargs.get('subtopic_name')
        topic_id = self.kwargs.get('topic_id')
        #Passing topic_name for display purpose on the template only
        topic_name=self.kwargs.get('topic_name')
        secure_topic = get_object_or_404(Topic.objects.filter(owner=self.request.user), id=topic_id)

        if subtopic_name=='goals_list':
            called_submodel= [subtopic_name, secure_topic.goal_set.all(), topic_name, topic_id]

        elif subtopic_name=='progress_list':
            called_submodel= [subtopic_name, secure_topic.progress_set.all(), topic_name, topic_id]

        elif subtopic_name=='mistakes_list':
            called_submodel= [subtopic_name, secure_topic.mistake_set.all(), topic_name, topic_id]

        return called_submodel

@login_required
def secure_subtopic_detail(request, **kwargs):
    """View secure subtopic detail"""

    subtopic_id= kwargs.get('subtopic_id')
    subtopic_name=kwargs.get('subtopic_name')
    topic_id=kwargs.get('topic_id')

    if subtopic_name=='goals_list':
        filtered_submodel = Goal.objects.filter(topic__owner=request.user)
        detail = get_object_or_404(filtered_submodel, id=subtopic_id)

    if subtopic_name=='progress_list':
        filtered_submodel = Progress.objects.filter(topic__owner=request.user)
        detail = get_object_or_404(filtered_submodel, id=subtopic_id)

    if subtopic_name=='mistakes_list':
        filtered_submodel = Mistake.objects.filter(topic__owner=request.user)
        detail = get_object_or_404(filtered_submodel, id=subtopic_id)

    context = {'detail': detail, 'subtopic_name':subtopic_name, 'topic_id':topic_id}

    return render(request, 'workout_tracker/secure_entry_detail.html', context)

@login_required
def add_topic(request):
    '''Adding Topic entry'''
    if request.method !='POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form= TopicForm(request.POST)
        if form.is_valid():
            new_topic= form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('awt:secure_topics_list')
    context={'form':form}
    return render(request, 'workout_tracker/add_topic.html', context)

@login_required
def delete_topic(request, topic_id):
    '''Deleting topic entry'''
    topic = Topic.objects.get(id=topic_id)
    if topic.owner == request.user:
        topic.delete()
        return redirect('awt:secure_topics_list')
    else:
        raise Http404


@login_required
def add_subtopic(request, topic_id, subtopic):
    '''Editing topic entry and redirecting to subtopic_list page'''

    topic = Topic.objects.get(id=topic_id)
    if topic.owner == request.user:

        if request.method != 'POST':
            # No data, create a blank form Check the subtopic_name, and generate the relevant form##
            if subtopic == 'goals_list':
                subtopic_form = GoalForm()
            elif subtopic == 'progress_list':
                subtopic_form = ProgressForm()
            elif subtopic == 'mistakes_list':
                subtopic_form = MistakeForm()

        else:
            # Post data submitted, process the form on the relevant form
            if subtopic == 'goals_list':
                subtopic_form = GoalForm(request.POST)
            elif subtopic == 'progress_list':
                subtopic_form = ProgressForm(request.POST)
            elif subtopic == 'mistakes_list':
                subtopic_form = MistakeForm(request.POST)

            if subtopic_form.is_valid():
                new_subtopic_form = subtopic_form.save(commit=False)
                new_subtopic_form.topic = topic
                new_subtopic_form.save()

                return redirect('awt:secure_subtopic_list', topic_name=topic, topic_id=topic_id, subtopic_name=subtopic)

        context = {'subtopic_form': subtopic_form, 'topic': topic, 'subtopic': subtopic}
        # Passing topic:topic here to generate topic.id required for submitting the form.
        return render(request, 'workout_tracker/add_subtopic.html', context)

    else:
        # User is not authorised
        raise Http404

@login_required
def edit_subtopic(request, subtopic_id, subtopic_name):
    '''Editing topic entry and redirecting to subtopic_detail page: which needs subtopic_id, subtopic_name, topic_id kwarg'''
    if request.method != 'POST':
        if subtopic_name == 'goals_list':
            subtopic = Goal.objects.get(id=subtopic_id)
            if subtopic.topic.owner == request.user:
                subtopic_form = GoalForm(instance=subtopic)

        elif subtopic_name == 'progress_list':
            subtopic = Progress.objects.get(id=subtopic_id)
            if subtopic.topic.owner == request.user:
                subtopic_form = ProgressForm(instance=subtopic)

        elif subtopic_name == 'mistakes_list':
            subtopic = Mistake.objects.get(id=subtopic_id)
            if subtopic.topic.owner == request.user:
                subtopic_form = MistakeForm(instance=subtopic)
    else:
        if subtopic_name == 'goals_list':
            subtopic = Goal.objects.get(id=subtopic_id)
            if subtopic.topic.owner == request.user:
                subtopic_form = GoalForm(instance=subtopic, data=request.POST)

        elif subtopic_name == 'progress_list':
            subtopic = Progress.objects.get(id=subtopic_id)
            if subtopic.topic.owner == request.user:
                subtopic_form = ProgressForm(instance=subtopic, data=request.POST)

        elif subtopic_name == 'mistakes_list':
            subtopic = Mistake.objects.get(id=subtopic_id)
            if subtopic.topic.owner == request.user:
                subtopic_form = MistakeForm(instance=subtopic, data=request.POST)
        try:
            if subtopic_form.is_valid():
                subtopic_form.save()

            return redirect('awt:secure_subtopic_detail', topic_id=subtopic.topic.id, subtopic_name=subtopic_name,subtopic_id=subtopic_id)
        except UnboundLocalError:
            #This will be raised cos subtopic_form will be unbound variable which is called before being reference, if the user is not authorised.
            raise Http404

    try:
        context = {'subtopic_form':subtopic_form, 'subtopic_name':subtopic_name, 'subtopic_id':subtopic_id}
        return render(request, 'workout_tracker/edit_subtopic.html', context)
    except UnboundLocalError:
        # This will be raised cos subtopic_form will be unbound variable which is called before being reference, if the user is not authorised.
        raise Http404

@login_required
def delete_subtopic(request, subtopic_id, subtopic_name):
    '''Deleting subtopic entry'''
    if subtopic_name=='goals_list':
        subtopic = Goal.objects.get(id=subtopic_id)
    elif subtopic_name=='progress_list':
        subtopic = Progress.objects.get(id=subtopic_id)
    elif subtopic_name=='mistakes_list':
        subtopic = Mistake.objects.get(id=subtopic_id)

    if subtopic.topic.owner == request.user:
        subtopic.delete()
        return redirect('awt:secure_subtopic_list', topic_name=subtopic.topic, topic_id=subtopic.topic.id, subtopic_name=subtopic_name)
    else:
        raise Http404



