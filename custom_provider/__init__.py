import logging

from faker.providers import BaseProvider
from faker.providers import date_time

from datetime import datetime
from dateutil.parser import parse as date_parse

logger = logging.getLogger()

# Setup the faker variable
# Faker provider for assignment
class CustomProvider(BaseProvider):
    def assignment(self):
        # Fake class list
        classes = [
            'Reading',
            'Video',
            'Practice',
            'Random',
            'English',
            'Architecture',
            'Information'
        ]
        num = self.random_number(digits=3)
        clas = self.random_element(elements=(*classes,))
        return '{0} Assignment #{1}'.format(clas, num)

    def date_time_on_date(self, date):
        """
        Input: datetime (or str that will be parsed)
        Output: datetime with a different time on the same date
        """

        #Try to convert it from a string, if it can't be converted just return the value
        try:
            if isinstance(date, str):
                date = date_parse(date)
            day = date.date()
            start = datetime(day.year, day.month, day.day)
            end = datetime(day.year, day.month, day.day, 23, 59, 59)
            return self.generator.date_time_between_dates(datetime_start=start, datetime_end=end)

        except:
            logger.warning(f"Exception for date of {date}, just returning original date")
            return date