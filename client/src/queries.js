import {gql} from 'apollo-boost';

export const GET_ALL_PEOPLE_WITH_RELATIONS = gql`
    query {
        people_with_parents {
            person{
              name
              birthdate
              gender
            }
            parents{
              name
            }
            married_with{
              name
            }
        }
      }`

const ADD_PERSON = gql`
    mutation{
        create_person(person_input: {name: name, birthdate: birthdate, gender, gender}) {
            update_person{
                name
                birthdate
                gender
            }
        }
    }`

export {GET_ALL_PEOPLE_WITH_RELATIONS}