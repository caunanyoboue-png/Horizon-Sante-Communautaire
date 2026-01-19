from django.test import TestCase
from django.contrib.auth import get_user_model
from messaging.models import Thread, Message

User = get_user_model()

class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1", password="pw1")
        self.user2 = User.objects.create_user(username="u2", password="pw2")

    def test_thread_creation(self):
        thread = Thread.objects.create(sujet="Consultation")
        thread.participants.add(self.user1, self.user2)
        
        self.assertEqual(thread.participants.count(), 2)
        
    def test_message_sending(self):
        thread = Thread.objects.create(sujet="Consultation")
        thread.participants.add(self.user1, self.user2)
        
        msg = Message.objects.create(
            thread=thread,
            sender=self.user1,
            contenu="Bonjour Docteur"
        )
        
        self.assertEqual(thread.messages.count(), 1)
        self.assertEqual(msg.sender, self.user1)
