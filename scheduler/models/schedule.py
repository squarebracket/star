class SemesterSchedule:
    def __init__(self):
        """
        Constructor for creating a schedule specific to a semester
        """
        self.schedule_items = []
        """:type :list[ScheduleItem]"""
        return

    def has_no_conflict_with(self, section):
        """
        Checks if the section's lab and lectures and tutorials
        have conflict with anything else in the schedule
        @type section:Section
        """
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
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Mon'],
                      key=lambda x: x.start_time)

    @property
    def tue_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Tue'],
                      key=lambda x: x.start_time)

    @property
    def wed_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Wed'],
                      key=lambda x: x.start_time)

    @property
    def thu_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Thu'],
                      key=lambda x: x.start_time)

    @property
    def fri_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Fri'],
                      key=lambda x: x.start_time)

    @property
    def sat_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Sat'],
                      key=lambda x: x.start_time)

    @property
    def sun_items(self):
        return sorted([item for item in self.schedule_items if item.day_of_week == 'Sun'],
                      key=lambda x: x.start_time)


class Schedule:
    def __init__(self):
        self.schedule_by_semester = {}
        """:type :dict[Semester, SemesterSchedule]"""
        return

    def add_schedule_item(self, item, semester):
        """
        Adds a schedule item to the list for the semester
        @type item:ScheduleItem
        @type semester:Semester
        """
        if semester not in self.schedule_by_semester:
            self.schedule_by_semester[semester] = SemesterSchedule()

        self.schedule_by_semester[semester].schedule_items.append(item)

    def add_section(self, section):
        """
        Add all the lectures, tutorials and labs for a section
        to the schedule
        @type section:Section
        """
        for lecture in section.lectures:
            self.add_schedule_item(lecture, section.semester_year)
        for tutorial in section.tutorials:
            self.add_schedule_item(tutorial, section.semester_year)
        for lab in section.labs:
            self.add_schedule_item(lab, section.semester_year)

    def has_no_conflict_with(self, section):
        """
        Checks if the schedule is in conflict with the section
        @type section:Section
        """
        if section.semester_year not in self.schedule_by_semester:
            return True
        else:
            return self.schedule_by_semester[section.semester_year].has_no_conflict_with(section)

    def clear(self):
        self.schedule_by_semester.clear()

    @property
    def semester_schedules(self):
        return self.schedule_by_semester.values()