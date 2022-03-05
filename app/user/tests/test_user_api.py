from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')

TOKEN_URL = reverse('user:token')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    '''Test the users API (public)'''

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''Test Creating User With Valid Payload Is Successful'''

        payload = {
            'email' : 'johnddoe@email.com',
            'password' : 'ronaldo2012',
            'name' : 'John Doe'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        '''Test creating a user already exists'''

        payload = {
            'email' : 'johndoe@email.com',
            'password' : 'ronaldo2012'
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''Password should be more tha 5 characters'''

        payload = {
            'email' : 'johndoey@gmail.com',
            'password' : 'ro',
            'name' : 'John Doey'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email = payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''TEst that a token is created for the user'''

        payload = {
            'email' : 'arshadkhan@email.com',
            'password': 'ronaldo2012'
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_create_token_invalid_credentials(self):
        '''Test that token is not created is invalid credentails are given'''

        create_user(email='arshadkhan@email.com', password='ronaldo2012')

        payload = {
            'email' : 'arshadkhan@email.com',
            'password' : 'ronassa'
        }

        res = self.client.post(TOKEN_URL, payload)
        
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''Test that token is not create if user doesn't exists'''

        payload = {'email' : 'zareen56@gmail.com', 'password': 'testpass'}

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        '''Test that email and password are required'''

        res = self.client.post(TOKEN_URL, {'email': 'one', 'password' : ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)