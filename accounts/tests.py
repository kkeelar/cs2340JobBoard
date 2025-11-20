from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail

from .models import Conversation, Message, CandidateEmailLog, Profile


class MessagingEmailTests(TestCase):
	def setUp(self):
		User = get_user_model()
		# create users
		self.recruiter = User.objects.create_user(username='rec', password='pass')
		self.candidate = User.objects.create_user(username='cand', password='pass', email='cand@example.com')

		# Ensure profiles exist and set roles
		self.rec_profile = Profile.objects.get(user=self.recruiter)
		self.rec_profile.role = 'recruiter'
		self.rec_profile.save()

		self.cand_profile = Profile.objects.get(user=self.candidate)
		self.cand_profile.role = 'seeker'
		self.cand_profile.email = 'cand@example.com'
		self.cand_profile.save()

	def test_start_and_message(self):
		self.client.login(username='rec', password='pass')
		# start conversation
		resp = self.client.get(reverse('start_conversation', args=[self.candidate.username]))
		# GET should render compose form
		self.assertEqual(resp.status_code, 200)

		# POST to start_conversation to create the conversation and first message
		resp = self.client.post(reverse('start_conversation', args=[self.candidate.username]), {'body': 'Hello candidate'})
		# After successful post we redirect to conversation_detail
		self.assertEqual(resp.status_code, 302)
		conv = Conversation.objects.first()
		self.assertIsNotNone(conv)
		self.assertEqual(Message.objects.count(), 1)

	def test_email_candidate_creates_log_and_sends(self):
		self.client.login(username='rec', password='pass')
		# use locmem backend for tests
		with self.settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'):
			resp = self.client.post(reverse('email_candidate', args=[self.candidate.username]), {
				'subject': 'Test', 'body': 'Hello via email'
			})
			# redirect back to profile
			self.assertEqual(resp.status_code, 302)
			# an email was sent
			self.assertEqual(len(mail.outbox), 1)
			log = CandidateEmailLog.objects.first()
			self.assertTrue(log.success)

	def test_owner_can_edit_email_inline(self):
		# candidate edits their own email via the inline profile form
		self.client.login(username='cand', password='pass')
		new_email = 'newcand@example.com'
		# POST to the edit_profile view with only the profile email field
		resp = self.client.post(reverse('edit_profile'), {'email': new_email})
		# should redirect back to profile
		self.assertEqual(resp.status_code, 302)
		from django.contrib.auth import get_user_model
		User = get_user_model()
		user = User.objects.get(pk=self.candidate.pk)
		profile = Profile.objects.get(user=user)
		self.assertEqual(user.email, new_email)
		self.assertEqual(profile.email, new_email)
