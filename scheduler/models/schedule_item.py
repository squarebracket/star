from django.db import models
from uni_info.models.section import Section


class ScheduleItem(models.Model):
    section = models.ForeignKey(Section)

    def conflicts_with(self, other_item):
        if type(other_item) is ScheduleItem:
            other_item = other_item.section
        elif type(other_item) is not Section:
            #error
            return
        # check to see if the days overlap
        for day in self.section.days:
            if day in other_item.days:
                break
        else:
            # if the for loop completes without breaking, the days don't overlap
        """
        Returns True if there is a conflict with passed thing
        """
            return False
        if self.section.start_time <= other_item.start_time <= self.section.end_time:
            return True
        if self.section.start_time <= other_item.end_time <= self.section.end_time:
            return True
        if other_item.start_time <= self.section.start_time <= other_item.end_time:
            return True
        if other_item.start_time <= self.section.end_time <= other_item.end_time:
            return True

        return False

    def __unicode__(self):
        return "%s from %s to %s on %s for %s" % (self.section.location, self.section.start_time,
                                                  self.section.end_time, self.section.days, self.section)

    class Meta:
        def __init__(self):
            pass

        app_label = 'scheduler'
