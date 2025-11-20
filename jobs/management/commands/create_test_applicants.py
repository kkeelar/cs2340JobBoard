from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import Profile
from jobs.models import Job, JobApplication

class Command(BaseCommand):
    help = 'Create test applicants for recruiter1 with location coordinates'

    def handle(self, *args, **options):
        # Create or get recruiter1
        recruiter, created = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter1@example.com',
                'first_name': 'Recruiter',
                'last_name': 'One',
            }
        )
        
        if created:
            recruiter.set_password('recruiter1pass')
            recruiter.save()
            self.stdout.write(
                self.style.SUCCESS('Created recruiter1 (username: recruiter1, password: recruiter1pass)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('recruiter1 already exists')
            )

        # Ensure recruiter profile exists and set role
        recruiter_profile, created = Profile.objects.get_or_create(user=recruiter)
        if recruiter_profile.role != 'recruiter':
            recruiter_profile.role = 'recruiter'
            recruiter_profile.company_name = 'TechRecruiters Inc.'
            recruiter_profile.email = recruiter.email
            recruiter_profile.save()
            self.stdout.write(self.style.SUCCESS('Updated recruiter1 profile to recruiter role'))

        # Create or get some jobs for recruiter1
        jobs = []
        job_titles = [
            'Senior Software Engineer',
            'Frontend Developer',
            'Data Scientist',
        ]
        
        for title in job_titles:
            job, created = Job.objects.get_or_create(
                title=title,
                company='TechRecruiters Inc.',
                posted_by=recruiter_profile,
                defaults={
                    'description': f'Great opportunity for {title}. Join our amazing team!',
                    'location': 'San Francisco, CA',
                    'salary_min': 100000,
                    'salary_max': 150000,
                    'required_skills': 'Python, JavaScript, React',
                    'work_type': 'hybrid',
                    'contact_email': recruiter.email,
                    'is_active': True,
                }
            )
            jobs.append(job)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created job: {title}'))

        # Test applicants with different locations and coordinates
        applicants_data = [
            {
                'username': 'applicant_sf1',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'email': 'alice@example.com',
                'location': 'San Francisco, CA',
                'latitude': 37.7749,
                'longitude': -122.4194,
                'headline': 'Full Stack Developer',
                'skills': 'Python, Django, React, PostgreSQL',
            },
            {
                'username': 'applicant_sf2',
                'first_name': 'Bob',
                'last_name': 'Smith',
                'email': 'bob@example.com',
                'location': 'San Francisco, CA',
                'latitude': 37.7849,
                'longitude': -122.4094,
                'headline': 'Senior Frontend Engineer',
                'skills': 'JavaScript, React, TypeScript, Node.js',
            },
            {
                'username': 'applicant_sf3',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'email': 'charlie@example.com',
                'location': 'San Francisco, CA',
                'latitude': 37.7649,
                'longitude': -122.4294,
                'headline': 'Data Scientist',
                'skills': 'Python, Machine Learning, SQL, pandas',
            },
            {
                'username': 'applicant_ny1',
                'first_name': 'Diana',
                'last_name': 'Williams',
                'email': 'diana@example.com',
                'location': 'New York, NY',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'headline': 'Software Engineer',
                'skills': 'Java, Spring Boot, React, MongoDB',
            },
            {
                'username': 'applicant_ny2',
                'first_name': 'Eve',
                'last_name': 'Davis',
                'email': 'eve@example.com',
                'location': 'New York, NY',
                'latitude': 40.7228,
                'longitude': -74.0160,
                'headline': 'Full Stack Developer',
                'skills': 'Python, Django, JavaScript, PostgreSQL',
            },
            {
                'username': 'applicant_ny3',
                'first_name': 'Frank',
                'last_name': 'Miller',
                'email': 'frank@example.com',
                'location': 'New York, NY',
                'latitude': 40.7028,
                'longitude': -74.0060,
                'headline': 'Backend Engineer',
                'skills': 'Python, FastAPI, Redis, Docker',
            },
            {
                'username': 'applicant_ny4',
                'first_name': 'Grace',
                'last_name': 'Wilson',
                'email': 'grace@example.com',
                'location': 'New York, NY',
                'latitude': 40.7128,
                'longitude': -73.9960,
                'headline': 'React Developer',
                'skills': 'React, TypeScript, Redux, Jest',
            },
            {
                'username': 'applicant_austin1',
                'first_name': 'Henry',
                'last_name': 'Moore',
                'email': 'henry@example.com',
                'location': 'Austin, TX',
                'latitude': 30.2672,
                'longitude': -97.7431,
                'headline': 'DevOps Engineer',
                'skills': 'AWS, Docker, Kubernetes, Terraform',
            },
            {
                'username': 'applicant_austin2',
                'first_name': 'Ivy',
                'last_name': 'Taylor',
                'email': 'ivy@example.com',
                'location': 'Austin, TX',
                'latitude': 30.2772,
                'longitude': -97.7531,
                'headline': 'Python Developer',
                'skills': 'Python, Flask, SQLAlchemy, Git',
            },
            {
                'username': 'applicant_seattle1',
                'first_name': 'Jack',
                'last_name': 'Anderson',
                'email': 'jack@example.com',
                'location': 'Seattle, WA',
                'latitude': 47.6062,
                'longitude': -122.3321,
                'headline': 'Software Engineer',
                'skills': 'Java, Spring, React, MySQL',
            },
            {
                'username': 'applicant_seattle2',
                'first_name': 'Kate',
                'last_name': 'Thomas',
                'email': 'kate@example.com',
                'location': 'Seattle, WA',
                'latitude': 47.6162,
                'longitude': -122.3421,
                'headline': 'Full Stack Developer',
                'skills': 'Python, Django, Vue.js, PostgreSQL',
            },
            {
                'username': 'applicant_chicago1',
                'first_name': 'Liam',
                'last_name': 'Jackson',
                'email': 'liam@example.com',
                'location': 'Chicago, IL',
                'latitude': 41.8781,
                'longitude': -87.6298,
                'headline': 'Frontend Developer',
                'skills': 'JavaScript, React, Angular, CSS',
            },
            {
                'username': 'applicant_chicago2',
                'first_name': 'Maya',
                'last_name': 'White',
                'email': 'maya@example.com',
                'location': 'Chicago, IL',
                'latitude': 41.8881,
                'longitude': -87.6398,
                'headline': 'Data Engineer',
                'skills': 'Python, Spark, Airflow, SQL',
            },
            {
                'username': 'applicant_la1',
                'first_name': 'Noah',
                'last_name': 'Harris',
                'email': 'noah@example.com',
                'location': 'Los Angeles, CA',
                'latitude': 34.0522,
                'longitude': -118.2437,
                'headline': 'Software Engineer',
                'skills': 'Python, JavaScript, React, Node.js',
            },
            {
                'username': 'applicant_boston1',
                'first_name': 'Olivia',
                'last_name': 'Martin',
                'email': 'olivia@example.com',
                'location': 'Boston, MA',
                'latitude': 42.3601,
                'longitude': -71.0589,
                'headline': 'Full Stack Developer',
                'skills': 'Python, Django, React, PostgreSQL',
            },
            {
                'username': 'applicant_denver1',
                'first_name': 'Paul',
                'last_name': 'Thompson',
                'email': 'paul@example.com',
                'location': 'Denver, CO',
                'latitude': 39.7392,
                'longitude': -104.9903,
                'headline': 'Backend Developer',
                'skills': 'Python, FastAPI, MongoDB, Redis',
            },
        ]

        # Create applicants and applications
        created_applicants = 0
        created_applications = 0
        statuses = ['applied', 'review', 'interview', 'offer', 'closed']

        for i, applicant_data in enumerate(applicants_data):
            # Create user
            user, created = User.objects.get_or_create(
                username=applicant_data['username'],
                defaults={
                    'email': applicant_data['email'],
                    'first_name': applicant_data['first_name'],
                    'last_name': applicant_data['last_name'],
                }
            )
            
            if created:
                user.set_password('applicant123')
                user.save()
                created_applicants += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created applicant: {applicant_data['username']}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"Applicant {applicant_data['username']} already exists, updating profile...")
                )

            # Create or update profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = 'seeker'
            profile.location = applicant_data['location']
            profile.latitude = applicant_data['latitude']
            profile.longitude = applicant_data['longitude']
            profile.headline = applicant_data['headline']
            profile.skills = applicant_data['skills']
            profile.email = applicant_data['email']
            profile.bio = f"Experienced {applicant_data['headline']} based in {applicant_data['location']}."
            profile.save()

            # Create applications for each applicant to some jobs
            # Apply each applicant to 1-2 jobs randomly
            import random
            jobs_to_apply = random.sample(jobs, min(random.randint(1, 2), len(jobs)))
            
            for job in jobs_to_apply:
                application, created = JobApplication.objects.get_or_create(
                    job=job,
                    applicant=user,
                    defaults={
                        'status': statuses[i % len(statuses)],  # Cycle through statuses
                        'cover_note': f'Hi! I am very interested in the {job.title} position.',
                        'applied_date': timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
                    }
                )
                if created:
                    created_applications += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created/updated {created_applicants} applicants '
                f'with {created_applications} new applications!'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'\nApplicants are located in: San Francisco (3), New York (4), '
                f'Austin (2), Seattle (2), Chicago (2), Los Angeles (1), Boston (1), Denver (1)'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'\nLogin credentials:'
                f'\n   Recruiter: recruiter1 / recruiter1pass'
                f'\n   Applicants: [username] / applicant123'
            )
        )

