from django.core.management.base import BaseCommand
from courts.models import CourtType

class Command(BaseCommand):
    help = 'Populates the database with initial court types'

    def handle(self, *args, **options):
        court_types = [
            ('Padel', 'Standard Padel court'),
            ('Futbol 5', '5-a-side Football pitch'),
            ('Futbol 7', '7-a-side Football pitch'),
            ('Futbol 11', '11-a-side Football pitch'),
        ]
        for name, desc in court_types:
            ct, created = CourtType.objects.get_or_create(name=name, defaults={'description': desc})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created CourtType: {name}'))
            else:
                self.stdout.write(f'CourtType {name} already exists.')
