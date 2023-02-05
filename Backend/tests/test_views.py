from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from Backend.models import Announcement, Offer, User
from Backend.serializers import OfferSerializer


from datetime import datetime
import pytz
from django.utils import timezone

from importlib import import_module
from IGL import settings

import json

class SendOfferViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('send_offer', kwargs={'pk': 1})
        self.client = APIClient()

        # Create test users
        self.sender = User.objects.create(
        FirstName = "Sender",
        LastName = "Example",
        Email = "sender@gmail.com", 
        PfP = "",
        PhoneNumber = "0550555555",

        )
        self.receiver = User.objects.create(
        FirstName = "receiver",
        LastName = "Example",
        Email = "receiver@gmail.com", 
        PfP = "",
        PhoneNumber = "0550555555",
        )

        # Create test announcement
        timezone.activate(pytz.timezone("CET"))
        time = timezone.localtime(timezone.now())
        self.announcement = Announcement.objects.create(
            PubDate = time,
            Title ="Test Announcement",
            Description = "Test Desc",
            Price = 1,
            Area = 1,
            Type = "Test Type",
            Category = 1,
            Wilaya = "Wilaya",
            Commune = "Commune", 
            Adress = "Adresse",
            Owner=self.receiver
        )

    def test_send_offer_success(self):
        # Set request session to simulate authenticated user
        session = self.client.session
        session['email'] = self.sender.Email
        session.save()

        # Send a POST request to the view with valid data
        data = {'content': 'Test offer'}
        response = self.client.post(self.url, data=data)

        # Assert that the request was successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert that an Offer object was created with the correct data
        message = Offer.objects.get(announcement=self.announcement)
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.receiver, self.receiver)
        self.assertEqual(message.announcement, self.announcement)
        self.assertEqual(message.content, 'Test offer')

    def test_send_offer_announcement_not_found(self):
        # Send a POST request to the view with a non-existent announcement pk
        data = {'content': 'Test offer'}
        response = self.client.post(reverse('send_offer', kwargs={'pk': 999}), data=data)

        # Assert that the request returned a 404 status code
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_send_offer_no_content(self):
        # Set request session to simulate authenticated user
        session = self.client.session
        session['email'] = self.sender.Email
        session.save()

        # Send a POST request to the view with no content data
        response = self.client.post(self.url)

        # Assert that the request returned a 400 status code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_offer_not_authenticated(self):
        # Send a POST request to the view without setting the request session
        data = {'content': 'Test offer'}
        response = self.client.post(self.url, data=data)

        # Assert that the request returned a 401 status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        

class GetOffersTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.sender = User.objects.create(
        FirstName = "Sender",
        LastName = "Example",
        Email = "sender@gmail.com", 
        PfP = "",
        PhoneNumber = "0550555555",

        )
        self.receiver = User.objects.create(
        FirstName = "receiver",
        LastName = "Example",
        Email = "receiver@gmail.com", 
        PfP = "",
        PhoneNumber = "0550555555",
        )
        # Create test announcement
        timezone.activate(pytz.timezone("CET"))
        time = timezone.localtime(timezone.now())
        self.announcement = Announcement.objects.create(
            PubDate = time,
            Title ="Test Announcement",
            Description = "Test Desc",
            Price = 1,
            Area = 1,
            Type = "Test Type",
            Category = 1,
            Wilaya = "Wilaya",
            Commune = "Commune", 
            Adress = "Adresse",
            Owner=self.receiver
        )

        self.offer = Offer.objects.create(
            sender = self.sender,
            receiver = self.receiver,
            announcement = self.announcement,
            content = "This is an offer"
        )

    def test_get_offers_with_valid_session(self):
        # Set session data for the request 
        session = self.client.session
        session['email'] = self.receiver.Email
        session.save()

        # Make the request 
        response = self.client.get(reverse('get_offer'))

        # Assert that the response is 200 OK 
        self.assertEqual(response.status_code, 200)

        # Assert that the offer data is returned in the response 
        offers = OfferSerializer(Offer.objects, many=True).data 
        print(response)
        self.assertEqual(json.loads(response.content), offers)

    def test_get_offers_without_valid_session(self): 
         # Make the request without a valid session 
         response = self.client.get(reverse('get_offer')) 

         # Assert that the response is 401 Unauthorized 
         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ResponseOfferTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Create test users
        self.sender = User.objects.create(
        FirstName = "Sender",
        LastName = "Example",
        Email = "sender@gmail.com", 
        PfP = "",
        PhoneNumber = "0550555555",

        )
        self.receiver = User.objects.create(
        FirstName = "receiver",
        LastName = "Example",
        Email = "receiver@gmail.com", 
        PfP = "",
        PhoneNumber = "0550555555",
        )
        # Create test announcement
        timezone.activate(pytz.timezone("CET"))
        time = timezone.localtime(timezone.now())
        self.announcement = Announcement.objects.create(
            PubDate = time,
            Title ="Test Announcement",
            Description = "Test Desc",
            Price = 1,
            Area = 1,
            Type = "Test Type",
            Category = 1,
            Wilaya = "Wilaya",
            Commune = "Commune", 
            Adress = "Adresse",
            Owner=self.receiver
        )

        self.offer = Offer.objects.create(
            sender = self.sender,
            receiver = self.receiver,
            announcement = self.announcement,
            content = "This is an offer"
        )

    def test_response_offer_success(self):
        session = self.client.session
        session['email'] = self.receiver.Email
        session.save()

        response = self.client.post(reverse('response_offer', kwargs={'pk': self.offer.id}), {'content': 'some content for response'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_response_offer_failure(self):
        response = self.client.post(reverse('response_offer', kwargs={'pk': self.offer.id}), {'content': 'some content for response'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)