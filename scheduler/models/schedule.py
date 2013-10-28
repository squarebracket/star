class CalculatedSchedule:
    def __init__(self):
        self.schedule_items = []
        return

    def add_schedule_item(self, item):
        self.schedule_items.append(item)

    def add_section(self, section):
        for lecture in section.lectures:
            self.add_schedule_item(lecture)
        for tutorial in section.tutorials:
            self.add_schedule_item(tutorial)
        for lab in section.labs:
            self.add_schedule_item(lab)

    def has_no_conflict_with(self, section):

        for existing_item in self.schedule_items:
            for lecture in section.lectures:
                if existing_item.conflicts_with(lecture):
                    return False
            for tutorial in section.tutorials:
                if existing_item.conflicts_with(tutorial):
                    return False
            for lab in section.labs:
                if existing_item.conflicts_with(lab):
                    return False

        return True

    @property
    def mon_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Mon'], key=lambda x: x.start_time)

    @property
    def tue_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Tue'], key=lambda x: x.start_time)

    @property
    def wed_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Wed'], key=lambda x: x.start_time)

    @property
    def thu_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Thu'], key=lambda x: x.start_time)

    @property
    def fri_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Fri'], key=lambda x: x.start_time)

    @property
    def sat_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Sat'], key=lambda x: x.start_time)

    @property
    def sun_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Sun'], key=lambda x: x.start_time)
