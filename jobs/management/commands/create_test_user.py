from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = 'Create a test user for demonstration purposes'

    def handle(self, *args, **options):
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS('Created test user (username: testuser, password: testpass123)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Test user already exists')
            )

        # Ensure profile exists and update it
        profile, created = Profile.objects.get_or_create(user=user)
        if not profile.headline:
            profile.headline = "Full Stack Developer looking for new opportunities"
            profile.bio = "Passionate developer with 3 years of experience in web development. Love working with modern technologies and solving complex problems."
            profile.location = "San Francisco, CA"
            profile.skills = "Python, JavaScript, React, Django, PostgreSQL, AWS, Docker"
            profile.links = "https://linkedin.com/in/testuser, https://github.com/testuser"
            profile.save()
            self.stdout.write(
                self.style.SUCCESS('Updated test user profile with sample data')
            )

        self.stdout.write(
            self.style.SUCCESS('\nTest user credentials:')
        )
        self.stdout.write(f'Username: testuser')
        self.stdout.write(f'Password: testpass123')
        self.stdout.write(f'Email: test@example.com')
