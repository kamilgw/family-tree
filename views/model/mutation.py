import graphene
from graph_db.model.person_relations import PersonRelations, RelationshipType
from views.model.person_schema import PersonAttributes, PersonSchema


def input_to_dictionary(person_input):
    dictionary = {}
    for key in person_input:
        dictionary[key] = person_input[key]
    return dictionary


class InputRelationshipType(graphene.Enum):
    MARRIED = 1
    PARENT = 2


class UpdatePersonInput(graphene.InputObjectType, PersonAttributes):
    pass


class BasePersonMutation(graphene.Mutation):
    success = graphene.Boolean()
    updated_person = graphene.Field(lambda: PersonSchema)

    def mutate(self, info, person_input):
        input_data = input_to_dictionary(person_input)
        repository = PersonRelations(info.context.graph_db)
        person = repository.update_or_create(input_data)
        return BasePersonMutation(updated_person=person, success=True)


class AddRelationship(graphene.Mutation):
    class Arguments:
        from_name = graphene.String(required=True)
        to_name = graphene.String(required=True)
        relationship_type = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        from_name = kwargs.pop('from_name')
        to_name = kwargs.pop('to_name')
        relationship_type = kwargs.pop('relationship_type')
        repository = PersonRelations(info.context.graph_db)
        success = repository.add_relation(from_name, to_name, RelationshipType[relationship_type])
        return AddRelationship(success=success)


class UpdatePerson(BasePersonMutation):
    class Arguments:
        person_input = UpdatePersonInput(required=True)


class CreatePerson(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        birthdate = graphene.String()
        gender = graphene.String()

    success = graphene.Boolean()
    person = graphene.Field(lambda: PersonSchema)

    def mutate(self, info, name, birthdate, gender):
        person_input = {'name': name, 'birthdate': birthdate, 'gender': gender}
        repository = PersonRelations(info.context.graph_db)
        person = repository.update_or_create(person_input)
        return CreatePerson(person=person, success=True)


class Mutations(graphene.ObjectType):
    update_person = UpdatePerson.Field()
    create_person = CreatePerson.Field()
    add_relationship = AddRelationship.Field()
