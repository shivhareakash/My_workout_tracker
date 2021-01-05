from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Topic(models.Model):
    '''This model contains the main Topic, such as Muscle group: Biceps/Triceps/Glutes/Hams'''
    topic_name = models.CharField(max_length=100)
    date_added= models.DateTimeField(auto_now=True)
    ## Associating owner with each Topic
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    ## Make Topic Public or private
    view_option = models.BooleanField(default=True)

    def __str__(self):
        '''returning a string representation of this class'''
        return self.topic_name
    class Meta:
        ordering = ['-date_added']

class Goal(models.Model):
    '''This class will store the Goals linked to the Topic'''
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    summary = models.CharField(max_length=100)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''returning a string representation of this goal_text for this class'''
        return self.summary[:30]

    class Meta:
        ordering = ['-date_added']

class Progress(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    summary = models.CharField(max_length=100)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''returning a string representation of this goal_text for this class'''
        return self.summary[:30]

    class Meta:
        '''This will avoid plurization of this Progress class'''
        verbose_name_plural = "Progress"
        ordering=['-date_added']

class Mistake(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    summary = models.CharField(max_length=100)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''returning a string representation of this goal_text for this class'''
        return self.summary[:30]

    class Meta:
        ordering = ['-date_added']