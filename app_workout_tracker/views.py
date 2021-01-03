from django.shortcuts import render
from .models import Topic, Progress, Goal, Mistake
from django.shortcuts import get_object_or_404
from .forms import TopicForm, GoalForm, MistakeForm, ProgressForm

# Create your views here.

## Public Views ###
def public_topics_list(request):
    '''List view of all public topics'''
    public_topics = Topic.objects.filter(view_option=True)
    context = {'public_topics':public_topics}
    return render(request, 'workout_tracker/home.html', context)

def public_subtopic_list(request, topic_id, subtopic_name):
    '''Goal list of one of the public topics with topic_id
    This function takes topic_id and subtopic_name as arguments and render the appropriate subtopic accordingly'''

    public_topic = get_object_or_404(Topic.objects.filter(view_option=True), id=topic_id)

    all_sub_models = {
                      'goals_list': public_topic.goal_set.all(),
                      'progress_list':public_topic.progress_set.all(),
                      'mistakes_list':public_topic.mistake_set.all()
                      }
    context = {'called_submodel': all_sub_models[subtopic_name], 'subtopic_name':subtopic_name}
    return render(request,'workout_tracker/entry_list.html', context)


def public_subtopic_detail(request, subtopic_id, subtopic_name):

    public_goal_list = Goal.objects.filter(topic__view_option=True)
    public_mistake_list = Mistake.objects.filter(topic__view_option=True)
    public_progress_list = Progress.objects.filter(topic__view_option=True)

    all_sub_models= {
            'goal_list':get_object_or_404(public_goal_list, id=subtopic_id),
            'mistake_list':get_object_or_404(public_mistake_list, id=subtopic_id),
            'progress_list':get_object_or_404(public_progress_list, id=subtopic_id)
        }
    context = {'detail':all_sub_models[subtopic_name]}
    return render(request, 'workout_tracker/entry_detail.html', context)


## Secure Views ###


def private_topic_list(request):
    '''View Private topics'''
    pass

def private_topic_detail(request):
    '''View Private topics'''
    pass

def add_topic(request):
    '''Adding Topic entry'''
    pass

def delete_topic(request):
    '''Deleting topic entry'''
    pass

def edit_topic(request):
    '''Editing topic entry'''
    pass

