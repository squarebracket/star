
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