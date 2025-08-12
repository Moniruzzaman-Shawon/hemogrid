import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date

User = get_user_model()

class Command(BaseCommand):
    help = 'Load donors from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to donors JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                donors = json.load(f)
        except Exception as e:
            self.stderr.write(f"Failed to read file {json_file}: {e}")
            return

        created = 0
        skipped = 0

        for donor_data in donors:
            email = donor_data.get('email')
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'Skipping existing user: {email}'))
                skipped += 1
                continue

            password = donor_data.get('password', 'defaultpassword123')
            full_name = donor_data.get('full_name')
            age = donor_data.get('age')
            address = donor_data.get('address')
            last_donation_date = donor_data.get('last_donation_date')
            availability_status = donor_data.get('availability_status', True)
            blood_group = donor_data.get('blood_group')

            # Convert last_donation_date string to date object if present
            if last_donation_date:
                last_donation_date = parse_date(last_donation_date)

            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                age=age,
                address=address,
                last_donation_date=last_donation_date,
                availability_status=availability_status,
                blood_group=blood_group,
                is_verified=True,
                is_active=True,
            )
            created += 1
            self.stdout.write(self.style.SUCCESS(f'Created user: {email}'))

        self.stdout.write(self.style.SUCCESS(f'Done! Created: {created}, Skipped: {skipped}'))
