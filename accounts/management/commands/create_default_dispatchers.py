from django.core.management.base import BaseCommand

from accounts.models import User, UserRole


DEFAULT_USERS = [
    {
        "email": "main@example.com",
        "username": "main",
        "password": "pass1234",
        "role": UserRole.MAIN_DISPATCHER,
    },
    {
        "email": "dispatcher@example.com",
        "username": "dispatcher",
        "password": "pass1234",
        "role": UserRole.DISPATCHER,
    },
]


class Command(BaseCommand):
    help = "Create default main dispatcher and dispatcher users if they do not exist"

    def handle(self, *args, **options):
        created = 0
        for data in DEFAULT_USERS:
            user, was_created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "role": data["role"],
                },
            )
            if was_created:
                user.set_password(data["password"])
                user.save()
                created += 1
                self.stdout.write(self.style.SUCCESS(f"Created user {data['email']} ({data['role']})"))
            else:
                self.stdout.write(f"User {data['email']} already exists")
        if created == 0:
            self.stdout.write(self.style.WARNING("No new users created"))

