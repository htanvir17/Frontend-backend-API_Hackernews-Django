from django.test import SimpleTestCase, TestCase
from .models import ContributionAsk
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
user = User.objects.get(author_id=2)
# Create your tests here.
'''
class SimpleTests(SimpleTestCase): #SimpleTestCase testing without data
    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
'''

#testing with database
class CAModelTest(TestCase): #TestCase module which lets us create a sample database
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', email='test@email.com', password='secret')
        ContributionAsk.objects.create(title='Testing ask', author=self.user, text='just a test')

    #to check database field; any function that has the word test* at the beginning and exists in a tests.py file will be run when we execute the command python manage.py test
    def test_text_content(self):
        ca = ContributionAsk.objects.get(id=1)
        expected_object_name = f'{ca.text}'
        print(expected_object_name)
        self.assertEqual(expected_object_name, 'just a test')

#to check: python manage.py test
#it will give errors because this user has to be logged and other things