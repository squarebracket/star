from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from scraper.models import ConcordiaScraper


class Command(BaseCommand):
    help = 'Scrape data for courses from Concordia'
    args = 'none'

    option_list = BaseCommand.option_list + (
        make_option('--year',
                    action='store',
                    dest='year',
                    default=None,
                    help='Specify the academic year to scrape'),
    )

    def handle(self, *args, **options):
        scraper = ConcordiaScraper()
        if options['year'] is not None:
            scraper.scrape_sections(year=options['year'])
        else:
            scraper.scrape_sections()

        self.stdout.write('Scraped classes')