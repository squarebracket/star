from django.core.management.base import BaseCommand, CommandError

from scraper import functions
from scraper.models import ConcordiaScraper


class Command(BaseCommand):
    help = 'Scrape data for courses from Concordia'
    args = 'none'

    def handle(self, *args, **options):
        scraper = ConcordiaScraper()
        scraper.scrape_sections()

        self.stdout.write('Scraped classes')