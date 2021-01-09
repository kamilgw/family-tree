import graphene


class PersonAttributes:
    name = graphene.String(required=True)
    birthdate = graphene.String()
    gender = graphene.String()


class CreatePersonAttributes:
    name = graphene.String(required=True)
    birthdate = graphene.String(required=True)
    gender = graphene.String(required=True)


class PersonSchema(graphene.ObjectType, PersonAttributes):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
