from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create or reset superuser account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Superuser username')
        parser.add_argument('--password', type=str, default='admin', help='Superuser password')
        parser.add_argument('--email', type=str, default='admin@example.com', help='Superuser email')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        # Check if user exists
        user = User.objects.filter(username=username).first()

        if user:
            # Update existing user
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Superuser "{username}" updated successfully')
            )
        else:
            # Create new user
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Superuser "{username}" created successfully')
            )

        self.stdout.write(self.style.SUCCESS(f'✓ Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Ready to login at /admin/'))
