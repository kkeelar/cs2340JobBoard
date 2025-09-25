from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from jobs.models import Job
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate the database with sample job postings'

    def handle(self, *args, **options):
        # Create or get a superuser to post jobs
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@jobboard.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created admin user (username: admin, password: admin123)')
            )

        # Sample job data
        jobs_data = [
            {
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'description': '''Join our dynamic engineering team to build scalable web applications that serve millions of users. 
                
Responsibilities:
• Design and implement robust backend systems using modern technologies
• Collaborate with cross-functional teams to deliver high-quality features
• Mentor junior developers and contribute to technical architecture decisions
• Participate in code reviews and maintain high coding standards

What we offer:
• Competitive salary and equity package
• Flexible work arrangements and unlimited PTO
• Health, dental, and vision insurance
• Professional development budget
• Modern tech stack and cutting-edge projects''',
                'salary_min': 120000,
                'salary_max': 180000,
                'required_skills': 'Python, Django, PostgreSQL, AWS, Docker, Git, JavaScript, React',
                'work_type': 'hybrid',
                'visa_sponsorship': True,
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'contact_email': 'hiring@techcorp.com',
            },
            {
                'title': 'Frontend Developer',
                'company': 'StartupXYZ',
                'location': 'Remote',
                'description': '''We're looking for a passionate Frontend Developer to join our growing team and help build beautiful, user-friendly interfaces.

Key Responsibilities:
• Develop responsive web applications using React and TypeScript
• Work closely with designers to implement pixel-perfect UIs
• Optimize applications for maximum speed and scalability
• Write clean, maintainable code with comprehensive testing

Benefits:
• 100% remote work
• Flexible hours
• Stock options
• Health insurance
• Learning and development stipend''',
                'salary_min': 80000,
                'salary_max': 120000,
                'required_skills': 'JavaScript, React, TypeScript, HTML, CSS, Git, Jest, Figma',
                'work_type': 'remote',
                'visa_sponsorship': False,
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'contact_email': 'jobs@startupxyz.com',
            },
            {
                'title': 'Data Scientist',
                'company': 'DataDriven Solutions',
                'location': 'New York, NY',
                'description': '''Join our data science team to extract insights from large datasets and drive business decisions through advanced analytics.

What you'll do:
• Build machine learning models to solve complex business problems
• Analyze large datasets to identify trends and patterns
• Create data visualizations and reports for stakeholders
• Collaborate with engineering teams to deploy models in production

Requirements:
• Strong background in statistics and machine learning
• Experience with Python data science stack
• Knowledge of SQL and database systems
• Excellent communication skills''',
                'salary_min': 100000,
                'salary_max': 150000,
                'required_skills': 'Python, pandas, scikit-learn, SQL, Tableau, Machine Learning, Statistics, R',
                'work_type': 'onsite',
                'visa_sponsorship': True,
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'contact_email': 'careers@datadriven.com',
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudFirst Technologies',
                'location': 'Austin, TX',
                'description': '''Help us build and maintain robust cloud infrastructure that powers our applications at scale.

Responsibilities:
• Design and implement CI/CD pipelines
• Manage cloud infrastructure on AWS/Azure
• Monitor system performance and reliability
• Automate deployment and scaling processes
• Implement security best practices

We offer:
• Competitive compensation
• Comprehensive benefits package
• Professional growth opportunities
• Collaborative work environment''',
                'salary_min': 95000,
                'salary_max': 140000,
                'required_skills': 'AWS, Docker, Kubernetes, Terraform, Jenkins, Python, Linux, Git',
                'work_type': 'hybrid',
                'visa_sponsorship': False,
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'contact_email': 'devops@cloudfirst.tech',
            },
            {
                'title': 'Junior Web Developer',
                'company': 'WebAgency Pro',
                'location': 'Remote',
                'description': '''Perfect opportunity for new graduates or career changers to start their web development journey with a supportive team.

What you'll learn:
• Modern web development with HTML, CSS, and JavaScript
• Backend development with PHP or Node.js
• Working with databases and APIs
• Version control with Git
• Agile development methodologies

We provide:
• Mentorship from senior developers
• Training and certification opportunities
• Flexible remote work
• Career advancement path''',
                'salary_min': 50000,
                'salary_max': 70000,
                'required_skills': 'HTML, CSS, JavaScript, Git, PHP, MySQL, WordPress',
                'work_type': 'remote',
                'visa_sponsorship': False,
                'job_type': 'Full-time',
                'experience_level': 'Entry level',
                'contact_email': 'jobs@webagencypro.com',
            },
            {
                'title': 'Product Manager',
                'company': 'InnovateTech',
                'location': 'Seattle, WA',
                'description': '''Drive product strategy and roadmap for our flagship SaaS platform used by thousands of businesses.

Key Responsibilities:
• Define product vision and strategy
• Work with engineering and design teams
• Gather and analyze user feedback
• Prioritize features and manage backlog
• Coordinate product launches

Qualifications:
• 3+ years of product management experience
• Strong analytical and communication skills
• Experience with Agile/Scrum methodologies
• Technical background preferred''',
                'salary_min': 110000,
                'salary_max': 160000,
                'required_skills': 'Product Management, Agile, Scrum, Analytics, User Research, SQL, Jira',
                'work_type': 'hybrid',
                'visa_sponsorship': True,
                'job_type': 'Full-time',
                'experience_level': 'Senior',
                'contact_email': 'pm-jobs@innovatetech.com',
            },
            {
                'title': 'Mobile App Developer (React Native)',
                'company': 'MobileFirst Studios',
                'location': 'Los Angeles, CA',
                'description': '''Build amazing mobile experiences for iOS and Android using React Native and cutting-edge technologies.

What you'll do:
• Develop cross-platform mobile applications
• Integrate with REST APIs and third-party services
• Optimize app performance and user experience
• Collaborate with designers and backend developers
• Participate in app store deployment process

Benefits:
• Competitive salary and bonuses
• Health and wellness benefits
• Flexible PTO policy
• Tech stipend for equipment''',
                'salary_min': 85000,
                'salary_max': 125000,
                'required_skills': 'React Native, JavaScript, TypeScript, Redux, REST APIs, Git, iOS, Android',
                'work_type': 'onsite',
                'visa_sponsorship': False,
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'contact_email': 'mobile@mobilefirst.studio',
            },
            {
                'title': 'UX/UI Designer',
                'company': 'DesignForward',
                'location': 'Remote',
                'description': '''Create intuitive and beautiful user experiences for web and mobile applications.

Responsibilities:
• Design user interfaces and user experiences
• Create wireframes, prototypes, and mockups
• Conduct user research and usability testing
• Collaborate with developers to implement designs
• Maintain design systems and style guides

Requirements:
• Portfolio demonstrating UX/UI design skills
• Proficiency in design tools (Figma, Sketch, Adobe)
• Understanding of user-centered design principles
• Strong communication and collaboration skills''',
                'salary_min': 70000,
                'salary_max': 110000,
                'required_skills': 'Figma, Sketch, Adobe Creative Suite, User Research, Prototyping, HTML, CSS',
                'work_type': 'remote',
                'visa_sponsorship': False,
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'contact_email': 'design@designforward.com',
            },
            {
                'title': 'Cybersecurity Analyst',
                'company': 'SecureNet Corp',
                'location': 'Washington, DC',
                'description': '''Protect our organization and clients from cyber threats through monitoring, analysis, and incident response.

Key Duties:
• Monitor security events and alerts
• Investigate potential security incidents
• Implement security policies and procedures
• Conduct vulnerability assessments
• Provide security awareness training

Requirements:
• Bachelor's degree in cybersecurity or related field
• Security certifications (CISSP, CEH, etc.) preferred
• Experience with security tools and technologies
• Strong analytical and problem-solving skills''',
                'salary_min': 75000,
                'salary_max': 105000,
                'required_skills': 'Cybersecurity, SIEM, Incident Response, Network Security, Penetration Testing, Risk Assessment',
                'work_type': 'onsite',
                'visa_sponsorship': True,
                'job_type': 'Full-time',
                'experience_level': 'Mid-level',
                'contact_email': 'security@securenet.corp',
            },
            {
                'title': 'Marketing Coordinator (Part-time)',
                'company': 'Growth Marketing Co',
                'location': 'Chicago, IL',
                'description': '''Support our marketing team with campaigns, content creation, and analytics.

Responsibilities:
• Assist with social media management
• Create marketing content and materials
• Track and analyze campaign performance
• Coordinate marketing events and webinars
• Support email marketing campaigns

Perfect for:
• Students or recent graduates
• Career changers interested in marketing
• Someone looking for part-time flexibility''',
                'salary_min': 25000,
                'salary_max': 35000,
                'required_skills': 'Social Media, Content Creation, Google Analytics, Email Marketing, Adobe Creative Suite',
                'work_type': 'hybrid',
                'visa_sponsorship': False,
                'job_type': 'Part-time',
                'experience_level': 'Entry level',
                'contact_email': 'marketing@growthmarketing.co',
            },
        ]

        # Create jobs
        created_count = 0
        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults={
                    **job_data,
                    'posted_by': admin_user,
                    'posted_date': timezone.now() - timedelta(days=created_count),
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created job: {job.title} at {job.company}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Job already exists: {job.title} at {job.company}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new job postings!')
        )
