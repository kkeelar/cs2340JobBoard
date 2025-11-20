from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send a simple test email using current EMAIL settings. Usage: manage.py send_test_email --to you@example.com'

    def add_arguments(self, parser):
        parser.add_argument('--to', dest='to', required=True, help='Email address to send the test message to')
        parser.add_argument('--subject', dest='subject', default='Test email from JobBoard', help='Subject')
        parser.add_argument('--body', dest='body', default='This is a test email sent from the JobBoard app.', help='Body')

    def handle(self, *args, **options):
        to = options['to']
        subject = options['subject']
        body = options['body']
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        try:
            send_mail(subject, body, from_email, [to])
            self.stdout.write(self.style.SUCCESS(f'Sent test email to {to}'))
        except Exception as exc:
            raise CommandError(f'Failed to send test email: {exc}')
