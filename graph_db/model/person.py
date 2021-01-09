import datetime
from enum import Enum

from py2neo.ogm import Model, Property
from py2neo import NodeMatcher


class Person(Model):
    __primarykey__ = 'name'
    __primarylabel__ = 'Person_u6GwizdzK'
    name = Property()
    birthdate = Property()
    gender = Property()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError("{0} is an unknown property".format(key))

    def find(self, graph):
        return Person.match(graph, self.name).first()

    def find_all(self, graph):
        return Person.match(graph)

    def as_dict(self):
        return {
            'name': self.name,
            'birthdate': datetime.date.fromisoformat(str(self.birthdate)),
            'gender': self.gender
        }

    @classmethod
    def label(cls):
        return cls.__primarylabel__

    @classmethod
    def key(cls):
        return cls.__primarykey__

    @staticmethod
    def sort_list_as_dict(persons):
        person_dicts = [person.as_dict() for person in persons]
        return sorted(person_dicts, key=lambda k: k['name'])

    @staticmethod
    def all_properties():
        return Person(birthdate='2019-10-12').as_dict().keys()


class ValidationResult(Enum):
    ABSENT = 1
    VALID = 2
    INVALID = 3


class PersonValidator:

    @classmethod
    def validate_birthday(cls, **person_input):
        # if 'birthdate' in person_input:
        #     try:
        #         datetime.date.fromisoformat(person_input['birthdate'])
        #         return
        #     except ValueError:
        #         return ValidationResult.INVALID
        # else:
        #     return ValidationResult.ABSENT
        pass

    @classmethod
    def has_all_properties(cls, **person_input):
        attributes = Person.all_properties()
        invalid_attributes = []
        for attribute in attributes:
            if attribute not in person_input:
                invalid_attributes.append((attribute, ValidationResult.ABSENT))
            elif attribute in person_input and not person_input[attribute]:
                invalid_attributes.append((attribute, ValidationResult.INVALID))
        return invalid_attributes
