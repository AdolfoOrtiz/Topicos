from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from quickstart.models import Card

class MeEndpointTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='Password123!',
            first_name='Juan',
            last_name='Perez'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_unauthenticated_me_fails(self):
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_token_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'tester')
        self.assertEqual(response.data['email'], 'tester@example.com')
        self.assertEqual(response.data['first_name'], 'Juan')
        self.assertEqual(response.data['last_name'], 'Perez')
        self.assertEqual(response.data['auth_token'], self.token.key)

    def test_me_with_bearer_header(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.get('/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'tester')

    def test_me_api_endpoint_variation(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.get('/api/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'tester')

    def test_me_without_trailing_slash(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.get('/me')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'tester')

    def test_edit_user_via_patch(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.patch('/me/', {
            'first_name': 'Carlos',
            'last_name': 'Gomez'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Carlos')
        self.assertEqual(response.data['last_name'], 'Gomez')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Carlos')
        self.assertEqual(self.user.last_name, 'Gomez')

    def test_edit_user_via_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/me/', {
            'first_name': 'Alejandro'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Alejandro')
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Alejandro')

    def test_cannot_edit_other_user_even_if_id_provided(self):
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='Password123!',
            first_name='OriginalName'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.patch('/me/', {
            'id': other_user.id,
            'first_name': 'HackedName'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Only tester changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'HackedName')
        
        # Other user remains untouched
        other_user.refresh_from_db()
        self.assertEqual(other_user.first_name, 'OriginalName')

    def test_cannot_use_already_taken_email(self):
        User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Password123!'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.patch('/me/', {
            'email': 'user2@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


class ResetTokenTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tokenuser',
            email='tokenuser@example.com',
            password='Password123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_unauthenticated_reset_token_fails(self):
        response = self.client.post('/resettoken')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reset_token_success(self):
        old_key = self.token.key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {old_key}')
        response = self.client.post('/resettoken')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_key = response.data['token']
        self.assertNotEqual(new_key, old_key)
        
        # Verify in DB
        self.assertTrue(Token.objects.filter(user=self.user, key=new_key).exists())
        self.assertFalse(Token.objects.filter(key=old_key).exists())

        # Old token cannot access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {old_key}')
        me_old = self.client.get('/me/')
        self.assertEqual(me_old.status_code, status.HTTP_401_UNAUTHORIZED)

        # New token can access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_key}')
        me_new = self.client.get('/me/')
        self.assertEqual(me_new.status_code, status.HTTP_200_OK)
        self.assertEqual(me_new.data['username'], 'tokenuser')

    def test_reset_token_url_variations(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.post('/api/resettoken/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


class LogoutTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='logoutuser',
            email='logoutuser@example.com',
            password='Password123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_unauthenticated_logout_fails(self):
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        token_key = self.token.key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_key}')
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Sesión cerrada exitosamente. Token eliminado.')

        # Token was removed from DB
        self.assertFalse(Token.objects.filter(user=self.user).exists())

        # Old token no longer works
        response_me = self.client.get('/me/')
        self.assertEqual(response_me.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_url_variations(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        response = self.client.post('/api/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CardViewSetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='carduser',
            email='carduser@example.com',
            password='Password123!'
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_unauthenticated_card_access_fails(self):
        response = self.client.get('/cards/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_list_cards(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.key}')
        # Crear carta
        response = self.client.post('/cards/', {
            'nombre': 'Dragón Blanco',
            'descripcion': 'Monstruo legendario de ojos azules.'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Dragón Blanco')

        # Listar cartas
        response_list = self.client.get('/cards/')
        self.assertEqual(response_list.status_code, status.HTTP_200_OK)
        self.assertEqual(response_list.data['count'], 1)

