import datetime
from khal.settings import get_config
from khal.khalendar import CalendarCollection


class Calendars:
    """
        Calendars class are a class for a list of calendars available on your config.
        Also serves as a superclass for a Calendar class.
    """
    def __init__(self, config=None, date=datetime.datetime.now(), locale=None):
        self.config = config if config else get_config()
        self.date = date
        self.locale = locale if locale else self.config.get('locale')
        self.calendars = self.config.get('calendars')
        self.db = self.config.get('sqlite').get('path')
        self.calendar = CalendarCollection(calendars=self.calendars,
                                           dbpath=self.db,
                                           locale=self.locale)
        self.default = self.config.get('default').get('default_calendar')
        self._events()

    def _events(self):
        """
            Save in self.events all events from all calendars in a list of Event objects.
        """
        self.events = [
            Event(
                **{
                    i: getattr(ev, i)
                    for i in dir(ev)
                    if not callable(getattr(ev, i)) and not i.startswith("_")
                }) for ev in self._get_all_events()
        ]

    def _get_all_events(self, date=None):
        """
            Gets all events from all calendars on config in khal.Event format.
            Accepts a datetime object as parameter to show all events from that specific date.
        """
        return list(
            self.calendar.get_events_on(self.date if not date else date))

    def get_first_ev(self):
        return min(self.events())


class Calendar(Calendars):
    def __init__(self, name, **kwargs):
        """
            Gets a singular calendar by name.
            If name does not exist on config, raise an error and show available.
        """
        sep = '\n'  #  New line separator for f-strings
        super().__init__(**kwargs)
        if name not in self.calendars.keys():
            raise AttributeError(
                f'Calendar "{name}" not found in khal config.\nCalendars found:\n{sep.join(self.calendars.keys())}'
            )
        self.name = name
        self.cal = {name: self.calendars.get(name)}
        self.calendar = CalendarCollection(calendars=self.cal,
                                           dbpath=self.db,
                                           locale=self.locale)
        self.events = self._events


class Event:
    """
        Event class which holds aspects of a khal event.
    """
    def __init__(self,
                 summary,
                 start: datetime,
                 end,
                 location=None,
                 description=None,
                 **kwargs):
        self.summary = summary.encode().decode()
        self.start = start.strftime('%d/%m/%Y')
        self.end = end.strftime('%d/%m/%Y')
        self.location = location
        self.description = description
        # Set remaining kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __gt__(self, other):
        if type(other) is not Event:
            raise TypeError('other should be an object of class Event')
        return self.start > other.start

    def __str__(self):
        # Returns a string like "[NAME EVENT] [START HH:MM]-[END HH:MM]"
        return f'{self.summary} {str(self.start_local.time())[:5]}-{str(self.end_local.time())[:5]}'
