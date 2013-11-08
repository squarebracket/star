# __all__ = ["academic_institution", "academic_program", "academic_requirement", "building", "corequisite", "course",
#            "department", "faculty", "prequisite", "section", "semester"]
import modulefinder
import inspect
import sys
import os

#from uni_info.models.course import Course
#from uni_info.models.section import Section

current_module = sys.modules[__name__]

mod = modulefinder.ModuleFinder()

##to_import = mod.find_all_submodules(current_module)
#os.chdir(current_module.__path__[0])
#sys.path.append(current_module.__path__[0])
##print current_module.__path__[0]
##for submod in to_import:
##    __import__(submod)
##    for name, obj in inspect.getmembers(submod, inspect.isclass):
##        __import__(submod, globals(), locals(), name)
#
#for submod in __all__:
#    __import__(submod)
#    for name, obj in inspect.getmembers(submod, inspect.isclass):
#        __import__(submod, globals(), locals(), name)
#
##    from module

from uni_info.models.academic_institution import AcademicInstitution
from uni_info.models.academic_program import AcademicProgram
from uni_info.models.academic_requirement import AcademicRequirement
from uni_info.models.building import Building
from uni_info.models.course import Course
from uni_info.models.department import Department
from uni_info.models.facility import Facility
from uni_info.models.faculty import Faculty
from uni_info.models.requirement import Requirement
from uni_info.models.section import Section
from uni_info.models.semester import Semester