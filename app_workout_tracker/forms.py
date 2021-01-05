from django import forms
from .models import Topic, Goal, Progress, Mistake



class TopicForm(forms.ModelForm):
    '''Creating django form for Topic Model'''
    class Meta:
        model = Topic
        fields = ['topic_name', 'view_option']
        # Leaving the labels empty
        labels = {'topic_name': 'Add new Topic', 'view_option': 'Make Public'}

class ProgressForm(forms.ModelForm):
    '''Creating django form for Progress Model'''

    class Meta:
        model = Progress
        fields= ['summary', 'text']
        labels = {'summary':'','text':''}
        widgets = {'text': forms.Textarea(attrs={'cols':80})}

class GoalForm(forms.ModelForm):
    '''Creating django form for Goal Model'''

    class Meta:
        model = Goal
        fields = ['summary', 'text']
        labels = {'summary':'','text':''}
        widgets = {'text':forms.Textarea(attrs={'cols':80})}

class MistakeForm(forms.ModelForm):
    '''Creating django form for Mistake Model'''

    class Meta:
        model = Mistake
        fields = ['summary', 'text']
        labels = {'summary':'','text':''}
        widgets = {'text':forms.Textarea(attrs={'cols':80})}

