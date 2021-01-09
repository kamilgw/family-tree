import logging
from enum import Enum

from py2neo import Node, Relationship

from graph_db.model.person import Person, PersonValidator


class RelationshipType(Enum):
    MARRIED = 1
    PARENT = 2


class PersonRelations:
    def __init__(self, graph):
        self._graph = graph

    def _relative(self, name):
        return self.find_parents(name) + self.find_children(name)

    def find_relative(self, name):
        partner_query = f"MATCH (person:Person_u6GwizdzK {{name:'{name}'}})-[:MARRIED]-(partner) " \
                        f"RETURN partner"
        relatives = self._relative(name)
        partner_name = self._scan_result_set(self._graph.run(partner_query))
        # relatives of your partner are also your relatives
        if len(partner_name) > 0:
            return relatives + self._relative(partner_name[0].name)
        return relatives

    def _merge_relationship(self, relationship_type, from_person, to_person):
        relationship = Relationship.type(relationship_type.name)
        tx = self._graph.begin()
        from_node = Node(Person.label(), **from_person.as_dict())
        to_node = Node(Person.label(), **to_person.as_dict())
        new_relationship = relationship(from_node, to_node)
        tx.merge(new_relationship, Person.label(), Person.key())
        tx.push(new_relationship)
        tx.commit()

    def add_relation(self, from_person_name, to_person_name, relationship_type):
        if relationship_type == RelationshipType.MARRIED:
            partner_query = f"MATCH (person:Person_u6GwizdzK {{name:'{from_person_name}'}})-[:MARRIED]-(partner) " \
                            f"RETURN partner " \
                            f"UNION MATCH (person:Person_u6GwizdzK {{name:'{to_person_name}'}})-[:MARRIED]-(partner) " \
                            f"RETURN partner"
            partner_name = [person.name for person in self._scan_result_set(self._graph.run(partner_query))]
            if len(partner_name) > 0:
                if sorted([from_person_name, to_person_name]) == sorted(partner_name):
                    self._merge_relationship(relationship_type, self.find(from_person_name),
                                             self.find(to_person_name))
                    return True
                else:
                    print("BlAD")

        exiting_relationship = self.check_related(from_person_name, to_person_name)
        has_current_relationship = exiting_relationship[0]
        current_relatives_names = exiting_relationship[3]

        if has_current_relationship and not (
                relationship_type == RelationshipType.PARENT and from_person_name in current_relatives_names):
            print("BŁĄD")
        self._merge_relationship(relationship_type, exiting_relationship[1], exiting_relationship[2])
        return True

    def check_related(self, from_person_name, to_person_name):
        """
        check if two persons have any relatives in common
        """
        from_person = self.find(from_person_name)
        to_person = self.find(to_person_name)
        if not from_person:
            raise ValueError("person with {} name does not exist.".format(from_person_name))

        if not to_person:
            raise ValueError("person with {} name does not exist.".format(to_person_name))

        from_person_relatives_names = [person.name for person in self.find_relative(from_person_name)]
        to_person_relatives_names = [person.name for person in self.find_relative(to_person_name)]
        related_names = set(from_person_relatives_names).intersection(set(to_person_relatives_names))
        return len(related_names) > 0, from_person, to_person, related_names

    def update_or_create(self, person_input_dict):

        person = self.find(person_input_dict['name'])
        property_dict = {}
        if not person:
            properties_validation = PersonValidator.has_all_properties(**person_input_dict)
            if len(properties_validation) > 0:
                properties = Person.all_properties()
                raise ValueError("new person requires all properties: " + ",".join(properties))
        else:
            property_dict = person.as_dict()

        for key, value in person_input_dict.items():
            property_dict[key] = value
        tx = self._graph.begin()
        node = Node(Person.label(), **property_dict)
        tx.merge(node, Person.label(), Person.key())
        tx.push(node)
        tx.commit()
        return self.find(property_dict['name'])

    def find(self, name):
        person = Person(name=name).find(self._graph)
        return person

    def find_people(self):
        people = Person().find_all(self._graph)
        return people

    def find_list(self, names):
        return [self.find(name) for name in names]

    def find_parents(self, name):
        cousins_query = f"MATCH (person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT]-(parent) RETURN parent " \
                        f"UNION MATCH (person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT]-(by_marriage)-" \
                        f"[:MARRIED]-(parent) RETURN parent"
        return self._scan_result_set(self._graph.run(cousins_query))

    def find_partner(self, name):
        partner_query = f"MATCH (person:Person_u6GwizdzK {{name:'{name}'}})-[:MARRIED]-(partner) " \
                        f"RETURN partner"
        return self._scan_result_set(self._graph.run(partner_query))

    def find_children(self, name):
        children_query = f"MATCH (person:Person_u6GwizdzK{{name:'{name}'}})-[:MARRIED]-(partner)-[:PARENT]->(children) " \
                         f"RETURN children UNION MATCH (person:Person_u6GwizdzK{{name:'{name}'}})-[:PARENT]->(children) " \
                         f"RETURN children"
        return self._scan_result_set(self._graph.run(children_query))

    def find_grandparents(self, name):
        cousins_query = f"MATCH (person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT*2]-(grandparent) " \
                        f"RETURN grandparent UNION MATCH " \
                        f"(person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT*2]-" \
                        f"(grand_by_marriage)-[:MARRIED]-(grandparent) RETURN grandparent"
        return self._scan_result_set(self._graph.run(cousins_query))

    def find_cousins(self, name):
        cousins_query = f"MATCH (person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT*2]-(grandparent)-[:PARENT]->" \
                        f"(sibling)-[:MARRIED]-(partner)<-[:PARENT]-(partner_parents)-[:PARENT]->(partner_sibling)-" \
                        f"[:PARENT]->(cousins) RETURN cousins UNION MATCH (person:Person_u6GwizdzK{{name:'{name}'}})" \
                        f"<-[:PARENT*2]-(grandparent), (grandparent)-[:PARENT]->(sibling)-[:PARENT]->(cousins)" \
                        f" RETURN cousins"

        return self._scan_result_set(self._graph.run(cousins_query))

    def find_siblings(self, name):
        siblings_query = f"MATCH (person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT]-(parent)-[:PARENT]->(sibling) " \
                         f"RETURN sibling UNION MATCH (person:Person_u6GwizdzK{{name:'{name}'}})<-[:PARENT]" \
                         f"-(parent)-[:MARRIED]-(partner)-[:PARENT]->(sibling) " \
                         f"WHERE NOT(sibling.name = '{name}') RETURN  sibling"
        return self._scan_result_set(self._graph.run(siblings_query))

    def _scan_result_set(self, result_set):
        result = []
        while result_set.forward():
            current = result_set.current
            for value in current.values():
                result.append(Person(name=value['name'],
                                     birthdate=value['birthdate'],
                                     gender=value['gender']))

        return result
