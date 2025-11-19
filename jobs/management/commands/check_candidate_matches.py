"""
Management command to check for new candidate matches for saved searches
and send email notifications to recruiters.

Run this command periodically (e.g., via cron) to check for new matches.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from jobs.models import SavedCandidateSearch, CandidateSearchMatch
from jobs.search_utils import find_new_matches_for_search, create_matches_for_search
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Check for new candidate matches for saved searches and send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without sending emails or creating matches',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No emails will be sent, no matches will be created'))

        # Get all active saved searches
        active_searches = SavedCandidateSearch.objects.filter(is_active=True)
        
        total_new_matches = 0
        total_notifications_sent = 0

        for search in active_searches:
            self.stdout.write(f'\nChecking search: "{search.name}" (ID: {search.pk})')
            
            # Find new matches
            new_candidates = find_new_matches_for_search(search)
            
            if not new_candidates:
                self.stdout.write(f'  No new matches found')
                continue

            self.stdout.write(f'  Found {len(new_candidates)} new match(es)')
            total_new_matches += len(new_candidates)

            if not dry_run:
                # Create match records
                matches_created = create_matches_for_search(search, new_candidates)
                self.stdout.write(f'  Created {matches_created} match record(s)')

                # Get the newly created matches that need notification
                new_matches = CandidateSearchMatch.objects.filter(
                    saved_search=search,
                    notified=False
                ).select_related('candidate__user')

                if new_matches.exists():
                    # Send email notification
                    recruiter = search.recruiter
                    recruiter_email = recruiter.email or recruiter.user.email
                    
                    if recruiter_email:
                        try:
                            self._send_notification_email(
                                recruiter_email,
                                recruiter.user.username,
                                search,
                                new_matches
                            )
                            
                            # Mark matches as notified
                            new_matches.update(notified=True, notified_date=timezone.now())
                            search.last_notified = timezone.now()
                            search.save(update_fields=['last_notified'])
                            
                            total_notifications_sent += 1
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✓ Sent notification email to {recruiter_email}')
                            )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ✗ Failed to send email: {str(e)}')
                            )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠ No email address for recruiter {recruiter.user.username}')
                        )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {total_new_matches} new matches found, '
                f'{total_notifications_sent} notification(s) sent'
            )
        )

    def _send_notification_email(self, recipient_email, recruiter_username, saved_search, matches):
        """Send email notification about new candidate matches"""
        subject = f'New Candidate Matches for "{saved_search.name}"'
        
        # Create email content
        match_list = []
        for match in matches[:10]:  # Limit to 10 in email
            candidate = match.candidate
            match_list.append({
                'name': candidate.user.get_full_name() or candidate.user.username,
                'headline': candidate.headline or '',
                'location': candidate.location or '',
                'profile_url': f'{settings.SITE_URL if hasattr(settings, "SITE_URL") else "http://localhost:8000"}/accounts/u/{candidate.user.username}/',
            })
        
        message = f"""
Hello {recruiter_username},

We found {matches.count()} new candidate(s) that match your saved search "{saved_search.name}".

"""
        for i, match_info in enumerate(match_list, 1):
            message += f"{i}. {match_info['name']}"
            if match_info['headline']:
                message += f" - {match_info['headline']}"
            if match_info['location']:
                message += f" ({match_info['location']})"
            message += f"\n   View profile: {match_info['profile_url']}\n\n"

        if matches.count() > 10:
            message += f"\n... and {matches.count() - 10} more match(es).\n"

        message += f"""
View all matches: {settings.SITE_URL if hasattr(settings, "SITE_URL") else "http://localhost:8000"}/jobs/searches/{saved_search.pk}/matches/

Best regards,
JobBoard Team
"""

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@jobboard.com',
            recipient_list=[recipient_email],
            fail_silently=False,
        )

