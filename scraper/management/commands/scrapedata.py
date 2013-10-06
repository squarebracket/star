from django.core.management.base import BaseCommand, CommandError

from scraper import functions


class Command(BaseCommand):
    help = 'Scrape data for courses from Concordia'
    args = 'none'

    def handle(self, *args, **options):
        functions.scrape_sections()

        self.stdout.write('Scraped classes')