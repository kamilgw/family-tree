import graphene
from graphql import GraphQLError

from graph_db.model.person import Person
from graph_db.model.person_relations import PersonRelations
from views.model.person_schema import PersonSchema


class PeopleWithRelations(graphene.ObjectType):
    person_name = graphene.String()
    person = graphene.Field(PersonSchema)
    parents = graphene.List(PersonSchema)
    married_with = graphene.List(PersonSchema)

    def resolve_person(self, info, **kwargs):
        repository = PersonRelations(info.context.graph_db)
        person = check_name(repository, self.person_name)
        return PersonSchema(**person.as_dict())

    def resolve_parents(self, info, **kwargs):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, self.person_name)
        return list_to_schema(repository.find_parents(self.person_name))

    def resolve_married_with(self, info, **kwargs):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, self.person_name)
        return list_to_schema(repository.find_partner(self.person_name))


class Query(graphene.ObjectType):
    people = graphene.List(PersonSchema)
    people_with_parents = graphene.List(PeopleWithRelations)
    updated_person = graphene.Field(PersonSchema, key=graphene.String())
    person = graphene.Field(lambda: PersonSchema, name=graphene.String())
    children = graphene.List(lambda: PersonSchema, name=graphene.String())
    parents = graphene.List(lambda: PersonSchema, name=graphene.String())
    siblings = graphene.List(lambda: PersonSchema, name=graphene.String())
    cousins = graphene.List(lambda: PersonSchema, name=graphene.String())
    grandparents = graphene.List(lambda: PersonSchema, name=graphene.String())

    def resolve_people(self, info, **kwargs):
        repository = PersonRelations(info.context.graph_db)
        return repository.find_people()

    def resolve_person(self, info, name):
        repository = PersonRelations(info.context.graph_db)
        person = check_name(repository, name)
        return PersonSchema(**person.as_dict())

    def resolve_people_with_parents(self, info):
        repository = PersonRelations(info.context.graph_db)
        peoples = repository.find_people()
        output = []
        for person in peoples:
            output.append(
                PeopleWithRelations(
                    person_name=person.name
                )
            )
        return output

    def resolve_parents(self, info, name):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, name)
        return list_to_schema(repository.find_parents(name))

    def resolve_children(self, info, name):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, name)
        return list_to_schema(repository.find_children(name))

    def resolve_siblings(self, info, name):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, name)
        return list_to_schema(repository.find_siblings(name))

    def resolve_cousins(self, info, name):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, name)
        return list_to_schema(repository.find_cousins(name))

    def resolve_grandparents(self, info, name):
        repository = PersonRelations(info.context.graph_db)
        check_name(repository, name)
        return list_to_schema(repository.find_grandparents(name))


def check_name(repository, name):
    person = repository.find(name)
    if person is None:
        raise GraphQLError("No person with name {}".format(name))
    return person


def list_to_schema(persons):
    person_dicts_sorted = Person.sort_list_as_dict(persons)
    return [PersonSchema(**person_dict) for person_dict in person_dicts_sorted]
