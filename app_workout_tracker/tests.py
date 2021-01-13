from django.db import models
from django.test import TestCase

# Create your tests here.
from .models import Topic, Goal, Progress, Mistake
from django.utils import timezone
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse


class ModelTest(TestCase):
    '''Class to check functioning of models'''

    def setUp(self):
        '''setUp function to create user before any test is created'''
        self.user1 = User.objects.create_user(username='test', email='test@test.com')
        self.user1.set_password('12345')
        self.user1.save()

        self.user2 = User.objects.create_user(username='gary', email='gary@gary.com')
        self.user2.set_password('12345')
        self.user2.save()

    def test_1_add_objects_as_owner(self):
        topic = Topic.objects.create(topic_name="test", owner=self.user2)
        Goal.objects.create(topic=topic, summary="test test", text="test test test")
        Progress.objects.create(topic=topic, summary="test1 test1", text="test1 test1 test1")
        Mistake.objects.create(topic=topic, summary="test2 test2", text="test2 test2 test2")

        self.assertEqual(Topic.objects.get(id=topic.id).topic_name, "test")
        self.assertEqual(Goal.objects.get(id=topic.id).summary, "test test")
        self.assertEqual(Progress.objects.get(id=topic.id).summary, "test1 test1")
        self.assertEqual(Mistake.objects.get(id=topic.id).summary, "test2 test2")

    def test_2_del_objects_as_owner(self):
        '''Checking if the topics could be deleted along with subtopics'''
        # Creating topics
        topic = Topic.objects.create(topic_name="test", owner=self.user1)
        goal = Goal.objects.create(topic=topic, summary="test test", text="test test test")
        progress = Progress.objects.create(topic=topic, summary="test1 test1", text="test1 test1 test1")
        Mistake.objects.create(topic=topic, summary="test2 test2", text="test2 test2 test2")

        # Deleting topics
        progress.delete()
        self.assertRaises(Progress.DoesNotExist, Progress.objects.get, id=progress.id)
        goal.delete()
        self.assertRaises(Goal.DoesNotExist, Goal.objects.get, id=goal.id)
        topic.delete()
        self.assertRaises(Topic.DoesNotExist, Topic.objects.get, id=topic.id)

    def test_3_add_objects_as_anoynous(self):
        '''Check if anonymous user can add topics'''
        self.assertRaises(ValueError, Topic.objects.create, topic_name="testing", owner=AnonymousUser())


class ViewsTest(TestCase):
    '''Class to check functioning of Views'''

    #################### Setup and Preparation before view test ###############
    def setUp(self):
        '''setUp function to create user before any test is created'''
        self.user1 = User.objects.create_user(username='test', email='test@test.com')
        self.user1.set_password('12345')
        self.user1.save()

        ###loging as user1
        login = self.client.login(username='test', password='12345')
        self.assertTrue(login)

        # Using views to add topic
        self.client.post(reverse('awt:add_topic'), {"topic_name": "TEST"})

        # Get Topic_id
        response1 = self.client.get(reverse('awt:secure_topics_list'))
        self.topic_id = response1.context['user_topics'][0].id
        self.topic_text = response1.context['user_topics'][0].topic_name

        # Adding subtopic
        # self.client.post(reverse("url or view", arguments/kwarguments), {dict containing post data})
        self.client.post(reverse('awt:add_subtopic', kwargs={"subtopic": "goals_list", "topic_id": self.topic_id}),
                         {"summary": "Goals_SUMMARY_TEST", "text": "TEXT_DETAIL1"})
        self.client.post(reverse('awt:add_subtopic', kwargs={"subtopic": "progress_list", "topic_id": self.topic_id}),
                         {"summary": "Progress_SUMMARY_TEST", "text": "TEXT_DETAIL2"})
        self.client.post(reverse('awt:add_subtopic', kwargs={"subtopic": "mistakes_list", "topic_id": self.topic_id}),
                         {"summary": "Mistakes_SUMMARY_TEST", "text": "TEXT_DETAIL3"})

    def second_user(self):
        '''This is to create a second user, however this method shall not be required in every test, hence not using setUp()'''
        self.user2 = User.objects.create_user(username='gary', email='gary@gmail.com')
        self.user2.set_password('12345')
        self.user2.save()

        # login as second user
        login = self.client.login(username='gary', password='12345')
        self.assertTrue(login)

        ##Adding second user's topic and getting its ID
        self.client.post(reverse('awt:add_topic'), {"topic_name": "user2_test"})
        response = self.client.get(reverse('awt:secure_topics_list'))
        self.topic2_id = response.context['user_topics'][0].id
        self.topic2_text = response.context['user_topics'][0].topic_name

        ## Adding subtopics
        self.goal_subtopic2 = self.client.post(
            reverse('awt:add_subtopic', kwargs={"subtopic": "goals_list", "topic_id": self.topic2_id}),
            {"summary": "Goals_summary_user2", "text": "textDetail1_user2"})
        self.progress_subtopic2 = self.client.post(
            reverse('awt:add_subtopic', kwargs={"subtopic": "progress_list", "topic_id": self.topic2_id}),
            {"summary": "Progress_summary_user2", "text": "textDetail2_user2"})
        self.mistake_subtopic2 = self.client.post(
            reverse('awt:add_subtopic', kwargs={"subtopic": "mistakes_list", "topic_id": self.topic2_id}),
            {"summary": "Mistakes_summary_user2", "text": "textDetail3_user2"})

    ############################### Testing as OWNER ######################################
    def test_4_add_and_view_topic_as_owner(self):
        '''create user, login and view entry'''

        # Verifying the post
        response = self.client.get(reverse('awt:secure_topics_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TEST")
        self.assertQuerysetEqual(response.context['user_topics'], ['<Topic: TEST>'])

    def test_5_delete_topic_as_owner(self):
        '''Delete topic as owner'''
        # Delete topic
        self.client.get(reverse('awt:delete_topic', args=[self.topic_id]))

        # Check if deleted
        response2 = self.client.get(reverse('awt:secure_topics_list'))
        self.assertContains(response2, "No new topic found")

    def test_6_add_view_delete_subtopic_list_as_owner(self):
        '''check if the owner can view and delete its own subtopics'''
        # View the subtopic
        subtopics = ["goals_list", "progress_list", "mistakes_list"]
        for subtopic in subtopics:
            response = self.client.get(reverse('awt:secure_subtopic_list',
                                               kwargs={"topic_id": self.topic_id, "topic_name": self.topic_text,
                                                       "subtopic_name": subtopic}))
            self.assertContains(response, "SUMMARY_TEST")

        # Delete the subtopics

        res = self.client.get(reverse('awt:delete_subtopic',
                                      kwargs={'subtopic_id': Goal.objects.get(summary="Goals_SUMMARY_TEST").id,
                                              'subtopic_name': "goals_list"}))
        self.assertEqual(res.status_code, 302)
        self.client.get(reverse('awt:delete_subtopic',
                                kwargs={'subtopic_id': Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id,
                                        'subtopic_name': "mistakes_list"}))
        self.client.get(reverse('awt:delete_subtopic',
                                kwargs={'subtopic_id': Progress.objects.get(summary="Progress_SUMMARY_TEST").id,
                                        'subtopic_name': "progress_list"}))

        # Check the subtopics
        for subtopic in subtopics:
            response = self.client.get(reverse('awt:secure_subtopic_list',
                                               kwargs={"topic_id": self.topic_id, "topic_name": self.topic_text,
                                                       "subtopic_name": subtopic}))
            self.assertContains(response, "There are no entries")

    def test_7_add_view_subtopic_detail_as_owner(self):
        '''Test to view if the subtopic_detail can be viewed by owner'''
        # subtopic was created in setUp function so verifying if that was is viewable.
        responses=[]
        responses.append(self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'topic_id':self.topic_id, 'subtopic_name':'goals_list',
                                        'subtopic_id':Goal.objects.get(summary="Goals_SUMMARY_TEST").id})))
        responses.append(self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'topic_id': self.topic_id, 'subtopic_name': 'goals_list',
                                        'subtopic_id': Progress.objects.get(summary="Progress_SUMMARY_TEST").id})))
        responses.append(self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'topic_id': self.topic_id, 'subtopic_name': 'goals_list',
                                        'subtopic_id': Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id})))
        for response in responses:
            self.assertContains(response, 'TEXT_DETAIL')


    def test_8_edit_subtopic_as_owner(self):
        '''Check to see if owner can edit entries'''

        # Edit topics
        self.client.post(reverse('awt:edit_subtopic',
                                 kwargs={'subtopic_id': Goal.objects.get(summary="Goals_SUMMARY_TEST").id,
                                         'subtopic_name': 'goals_list'}),
                         data={'summary': 'Biceps', 'text': '17Inches'})
        self.client.post(reverse('awt:edit_subtopic',
                                 kwargs={'subtopic_id': Progress.objects.get(summary="Progress_SUMMARY_TEST").id,
                                         'subtopic_name': 'progress_list'}),
                         data={'summary': 'Triceps', 'text': '18Inches'})
        self.client.post(reverse('awt:edit_subtopic',
                                 kwargs={'subtopic_id': Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id,
                                         'subtopic_name': 'mistakes_list'}),
                         data={'summary': 'Quads', 'text': '19Inches'})

        # Verify if they were modified
        subtopics = ["goals_list", "progress_list", "mistakes_list"]
        responses = []
        for subtopic in subtopics:
            responses.append(self.client.get(reverse('awt:secure_subtopic_list',
                                                     kwargs={"topic_id": self.topic_id, "topic_name": self.topic_text,
                                                             "subtopic_name": subtopic})))

        self.assertContains(responses[0], "Biceps")
        self.assertContains(responses[1], "Triceps")
        self.assertContains(responses[2], "Quads")

    ########################### Non-Owner ##############################
    def test_9_view_topic_as_non_owner(self):
        '''test to view if non_owner can view the topic'''
        self.second_user()
        response=self.client.get(reverse('awt:secure_topics_list'))
        #Ensuring only user_2 topics are displayed in the query.
        self.assertQuerysetEqual(response.context['user_topics'], ['<Topic: user2_test>'])


    def test_10_view_subtopic_list_and_delete_subtopic_as_Non_owner(self):
        '''test to check if non owner can delete subtopic_list item'''
        # Login as non owner and view the subtopic
        self.second_user()
        subtopics = ["goals_list", "progress_list", "mistakes_list"]
        for subtopic in subtopics:
            response = self.client.get(reverse('awt:secure_subtopic_list',
                                               kwargs={"topic_id": self.topic_id, "topic_name": self.topic_text,
                                                       "subtopic_name": subtopic}))
            self.assertEqual(response.status_code, 404)

        # Try to delete the subtopics

        res = self.client.get(reverse('awt:delete_subtopic',
                                      kwargs={'subtopic_id': Goal.objects.get(summary="Goals_SUMMARY_TEST").id,
                                              'subtopic_name': "goals_list"}))
        self.assertEqual(res.status_code, 404)
        res = self.client.get(reverse('awt:delete_subtopic',
                                      kwargs={'subtopic_id': Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id,
                                              'subtopic_name': "mistakes_list"}))
        self.assertEqual(res.status_code, 404)
        res = self.client.get(reverse('awt:delete_subtopic',
                                      kwargs={'subtopic_id': Progress.objects.get(summary="Progress_SUMMARY_TEST").id,
                                              'subtopic_name': "progress_list"}))
        self.assertEqual(res.status_code, 404)

        # Check the subtopics still exist
        self.client.logout()
        self.client.login(username='test', password=12345)
        for subtopic in subtopics:
            response = self.client.get(reverse('awt:secure_subtopic_list',
                                               kwargs={"topic_id": self.topic_id, "topic_name": self.topic_text,
                                                       "subtopic_name": subtopic}))
            self.assertContains(response, "SUMMARY_TEST")

    def test_11_view_subtopic_detail_as_non_owner(self):
        '''Check to see if a non_owner can view subtopic detail page'''
        self.second_user()
        # View the subtopic
        responses=[]
        responses.append(self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'subtopic_id':Goal.objects.get(summary='Goals_SUMMARY_TEST').id,
                                        'subtopic_name':'goals_list','topic_id':self.topic_id})))
        responses.append(self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'subtopic_id':Progress.objects.get(summary='Progress_SUMMARY_TEST').id,
                                        'subtopic_name':'progress_list','topic_id':self.topic_id})))
        responses.append(self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'subtopic_id': Mistake.objects.get(summary='Mistakes_SUMMARY_TEST').id,
                                        'subtopic_name': 'mistakes_list', 'topic_id': self.topic_id})))
        for response in responses:
            self.assertEqual(response.status_code, 404)


    def test_12_delete_topic_as_non_owner(self):
        '''Check to see if a non_owner can view_delete topic'''
        self.second_user()
        # Here self.topic_id belongs to first user
        response1 = self.client.get(reverse('awt:delete_topic', args=[self.topic_id]))
        self.assertEqual(response1.status_code, 404)

        # Check if still not deleted
        self.client.login(username='test', password='12345')
        response = self.client.get(reverse('awt:secure_topics_list'))
        self.assertContains(response, "TEST")

    def test13_edit_subtopic_as_non_owner(self):
        '''Check to see if non-owner can edit entries'''
        self.second_user()
        response = self.client.post(reverse('awt:edit_subtopic',
                                            kwargs={'subtopic_id': Goal.objects.get(summary="Goals_SUMMARY_TEST").id,
                                                    'subtopic_name': 'goals_list'}),
                                    data={'summary': 'Biceps', 'text': '17Inches'})

        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('awt:edit_subtopic',
                                            kwargs={
                                                'subtopic_id': Progress.objects.get(summary="Progress_SUMMARY_TEST").id,
                                                'subtopic_name': 'progress_list'}),
                                    data={'summary': 'Triceps', 'text': '18Inches'})
        self.assertEqual(response.status_code, 404)
        response = self.client.post(reverse('awt:edit_subtopic',
                                            kwargs={
                                                'subtopic_id': Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id,
                                                'subtopic_name': 'mistakes_list'}),
                                    data={'summary': 'Quads', 'text': '19Inches'})
        self.assertEqual(response.status_code, 404)

    ############################ Anoynoums user #################################
    def set_public_topic(self):
        self.user3 = User.objects.create_user(username='hary', email='hary@gmail.com')
        self.user3.set_password('12345')
        self.user3.save()

        # login as second user
        login = self.client.login(username='hary', password='12345')
        self.assertTrue(login)

        # Create topic which is public
        self.client.post(reverse('awt:add_topic'), data={"topic_name": "This is Public", "view_option": True})
        response=self.client.get(reverse('awt:public_topics_list'))
        self.topic3_id= response.context['public_topics'][0].id
        self.topic3_text=response.context['public_topics'][0].topic_name

        #Create subtopic which is public
        self.client.post(reverse('awt:add_subtopic', kwargs={'topic_id':self.topic3_id,'subtopic':'goals_list'}),
                         data={'summary':'public_summary_goal','text':'Public_text_goal'})
        self.client.post(reverse('awt:add_subtopic', kwargs={'topic_id': self.topic3_id, 'subtopic': 'progress_list'}),
                         data={'summary': 'public_summary_progress', 'text': 'Public_text_progress'})
        self.client.post(reverse('awt:add_subtopic', kwargs={'topic_id': self.topic3_id, 'subtopic': 'mistakes_list'}),
                         data={'summary': 'public_summary_mistake', 'text': 'Public_text_mistake'})

    def test_14_view_topic_when_not_loggedin(self):
        '''test to see if the topic could be added when not logged in.'''
        # Creating a topic with view_option=true
        self.set_public_topic()

        self.client.logout()
        # Ensuring anoynomous user can not access secure topics_list
        response = self.client.get(reverse('awt:secure_topics_list'))
        self.assertRedirects(response, expected_url='/users/login/?next=/secure_list/', status_code=302)

        response=self.client.get(reverse('awt:public_topics_list'))
        #Ensuring anoynmouse user can  public topics_list with view_option=False
        self.assertQuerysetEqual(response.context['public_topics'], ['<Topic: This is Public>'])
        data="Public"
        self.assertContains(response, "%s"%data)


    def test_15_add_topic_when_not_loggedin(self):
        '''test to see if secure and public topic could be added when not logged in'''
        self.client.logout()
        response = self.client.post(reverse('awt:add_topic'), data={"topic_name": "This is Public_POSTING", "view_option": True})
        self.assertRedirects(response, expected_url='/users/login/?next=/add_topic/', status_code=302)

    def test_16_add_subtopic_when_not_loggedin(self):
        '''test to see if secure and public subtopic could be added when not logged in'''
        self.set_public_topic()
        self.client.logout()

        response = self.client.post(
            reverse('awt:add_subtopic', kwargs={'topic_id': self.topic3_id, 'subtopic': 'goals_list'}))
        self.assertRedirects(response, expected_url='/users/login/?next=/add_subtopic/%d/goals_list' % self.topic3_id)

        response = self.client.post(
            reverse('awt:add_subtopic', kwargs={'topic_id': self.topic3_id, 'subtopic': 'mistakes_list'}))
        self.assertRedirects(response, expected_url='/users/login/?next=/add_subtopic/%d/mistakes_list' % self.topic3_id)

        response = self.client.post(
            reverse('awt:add_subtopic', kwargs={'topic_id': self.topic3_id, 'subtopic': 'progress_list'}))
        self.assertRedirects(response, expected_url='/users/login/?next=/add_subtopic/%d/progress_list' % self.topic3_id)

    def test_17_view_subtopic_list_when_not_loggedin(self):
        '''test to see if subtopic list can be seen when not loggedin '''
        self.set_public_topic()
        self.client.logout()

        #Ensuring Public subtopics_list is displayed
        response = self.client.get(
            reverse('awt:public_subtopic_list', kwargs={'topic_id': self.topic3_id, 'subtopic_name': 'goals_list'}))
        self.assertContains(response, "public_summary_goal")

        response = self.client.get(
            reverse('awt:public_subtopic_list', kwargs={'topic_id': self.topic3_id, 'subtopic_name': 'progress_list'}))
        self.assertContains(response, "public_summary_progress")

        response = self.client.get(
            reverse('awt:public_subtopic_list', kwargs={'topic_id': self.topic3_id, 'subtopic_name': 'mistakes_list'}))
        self.assertContains(response, "public_summary_mistake")

        # Ensuring private subtopics_list is NOT displayed
        response=self.client.get(reverse('awt:secure_subtopic_list', kwargs={'topic_id':self.topic_id, 'subtopic_name':'goals_list', 'topic_name':self.topic_text}))
        self.assertRedirects(response, expected_url='/users/login/?next=/secure_list/%d/subtopic_list/%s/goals_list/'%(self.topic_id, self.topic_text))

        response=self.client.get(reverse('awt:secure_subtopic_list', kwargs={'topic_id':self.topic_id, 'subtopic_name':'mistakes_list', 'topic_name':self.topic_text}))
        self.assertRedirects(response, expected_url='/users/login/?next=/secure_list/%d/subtopic_list/%s/mistakes_list/'%(self.topic_id, self.topic_text))

        response=self.client.get(reverse('awt:secure_subtopic_list', kwargs={'topic_id':self.topic_id, 'subtopic_name':'progress_list', 'topic_name':self.topic_text}))
        self.assertRedirects(response, expected_url='/users/login/?next=/secure_list/%d/subtopic_list/%s/progress_list/'%(self.topic_id, self.topic_text))

    def test_18_view_subtopic_details_when_not_loggedin(self):
        '''test to see if subtopic detail can be seen when not loggedin'''
        self.set_public_topic()
        self.client.logout()
        # View Public subtopics_detail  subtopic_id, subtopic_name
        response=self.client.get(reverse('awt:public_subtopic_detail', kwargs={'subtopic_id':Goal.objects.get(summary='public_summary_goal').id, 'subtopic_name':'goals_list'}))
        self.assertContains(response, 'Public_text_goal')

        response = self.client.get(reverse('awt:public_subtopic_detail',
                                           kwargs={'subtopic_id': Progress.objects.get(summary='public_summary_progress').id,
                                                   'subtopic_name': 'progress_list'}))
        self.assertContains(response, 'Public_text_progress')

        response = self.client.get(reverse('awt:public_subtopic_detail',
                                           kwargs={'subtopic_id': Mistake.objects.get(summary='public_summary_mistake').id,
                                                   'subtopic_name': 'mistakes_list'}))
        self.assertContains(response, 'Public_text_mistake')


        # View Private subtopics_detail
        response=self.client.get(reverse('awt:secure_subtopic_detail',
                                kwargs={'subtopic_name': 'goals_list', 'topic_id': self.topic_id,
                                        'subtopic_id': Goal.objects.get(summary='Goals_SUMMARY_TEST').id}))
        self.assertRedirects(response, status_code=302, expected_url='/users/login/?next=/secure_list/%d/goals_list/%d/'%(self.topic_id,Goal.objects.get(summary='Goals_SUMMARY_TEST').id))

        response = self.client.get(reverse('awt:secure_subtopic_detail',
                                           kwargs={'subtopic_name': 'progress_list', 'topic_id': self.topic_id,
                                                   'subtopic_id': Progress.objects.get(summary='Progress_SUMMARY_TEST').id}))
        self.assertRedirects(response, status_code=302,
                             expected_url='/users/login/?next=/secure_list/%d/progress_list/%d/' % (self.topic_id, Progress.objects.get(summary='Progress_SUMMARY_TEST').id))

        response = self.client.get(reverse('awt:secure_subtopic_detail',
                                           kwargs={'subtopic_name': 'mistakes_list', 'topic_id': self.topic_id,
                                                   'subtopic_id': Mistake.objects.get(summary='Mistakes_SUMMARY_TEST').id}))
        self.assertRedirects(response, status_code=302, expected_url='/users/login/?next=/secure_list/%d/mistakes_list/%d/' % (self.topic_id, Mistake.objects.get(summary='Mistakes_SUMMARY_TEST').id))

    def test19_edit_subtopic_when_not_loggedin(self):
        '''Check to see if non-owner can edit entries'''
        self.client.logout()
        response = self.client.post(reverse('awt:edit_subtopic',
                                            kwargs={'subtopic_id': Goal.objects.get(summary="Goals_SUMMARY_TEST").id,
                                                    'subtopic_name': 'goals_list'}),
                                    data={'summary': 'Biceps', 'text': '17Inches'})
        self.assertRedirects(response,
                             expected_url=('/users/login/?next=/edit_subtopic/%d/goals_list' % Goal.objects.get(
                                 summary="Goals_SUMMARY_TEST").id), status_code=302)

        response = self.client.post(reverse('awt:edit_subtopic',
                                            kwargs={
                                                'subtopic_id': Progress.objects.get(summary="Progress_SUMMARY_TEST").id,
                                                'subtopic_name': 'progress_list'}),
                                    data={'summary': 'Triceps', 'text': '18Inches'})
        self.assertRedirects(response,
                             expected_url=('/users/login/?next=/edit_subtopic/%d/progress_list' % Progress.objects.get(
                                 summary="Progress_SUMMARY_TEST").id),status_code=302)

        response = self.client.post(reverse('awt:edit_subtopic',
                                            kwargs={
                                                'subtopic_id': Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id,
                                                'subtopic_name': 'mistakes_list'}),
                                    data={'summary': 'Quads', 'text': '19Inches'})
        self.assertRedirects(response,
                             expected_url=('/users/login/?next=/edit_subtopic/%d/mistakes_list' %Mistake.objects.get(
                                 summary="Mistakes_SUMMARY_TEST").id), status_code=302)

    def test_20_delete_topic_when_not_loggedin(self):
        self.client.logout()
        response = self.client.post(reverse('awt:delete_topic', args=[self.topic_id]))
        self.assertEqual(response.status_code, 302)
        expected_url = ('/users/login/?next=/delete_topic/%d/' % self.topic_id)
        self.assertRedirects(response, expected_url=expected_url, target_status_code=200)

    def test_21_delete_subttopic_list_when_not_loggedin(self):
        '''Test to see if anonymous user can delete subtopics'''
        self.client.logout()

        response=self.client.get(reverse('awt:delete_subtopic', kwargs={'subtopic_id':Goal.objects.get(summary="Goals_SUMMARY_TEST").id, 'subtopic_name':'goals_list'}))
        self.assertRedirects(response, expected_url=('/users/login/?next=/delete_entry/goals_list/%d' %Goal.objects.get(summary="Goals_SUMMARY_TEST").id),status_code=302)

        response=self.client.get(reverse('awt:delete_subtopic', kwargs={'subtopic_id':Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id, 'subtopic_name':'mistakes_list'}))
        self.assertRedirects(response, expected_url=('/users/login/?next=/delete_entry/mistakes_list/%d' %Mistake.objects.get(summary="Mistakes_SUMMARY_TEST").id),status_code=302)

        response= self.client.get(reverse('awt:delete_subtopic', kwargs={'subtopic_id':Progress.objects.get(summary="Progress_SUMMARY_TEST").id, 'subtopic_name':'progress_list'}))
        self.assertRedirects(response, expected_url=('/users/login/?next=/delete_entry/progress_list/%d' %Progress.objects.get(summary="Progress_SUMMARY_TEST").id),status_code=302)



