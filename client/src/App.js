import React, {useState} from "react";
import "./App.css";
import {Graph} from "react-d3-graph";
import man from "./images/man.png"
import woman from "./images/woman.png"
import {
    MDBBtn,
    MDBCard,
    MDBCardBody,
    MDBCol,
    MDBContainer,
    MDBRow
} from "mdbreact";
import {gql, useMutation, useLazyQuery} from '@apollo/client';


const svgTable = {"MALE": man, "FEMALE": woman}

const GET_ALL_PEOPLE_WITH_RELATIONS = gql`
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
    mutation create_person($name: String!, $birthdate: String!, $gender: String!){
        create_person(name: $name, birthdate: $birthdate, gender: $gender) {
            success
        }
    }`

const ADD_RELATIONS = gql`
    mutation add_relationship($from_name: String!, $to_name: String!, $relationship_type: String!){
        add_relationship(from_name: $from_name, to_name: $to_name, relationship_type: $relationship_type) {
            success
        }
    }`

const GET_ALL_RELATIONS = gql`
    query PersonName($name: String!) {
        parents(name: $name) {
            name
            birthdate
        }
        children(name: $name) {
            name
            birthdate
        }
        grandparents(name: $name) {
            name
            birthdate
        }
        siblings(name: $name) {
            name
            birthdate
        }
        cousins(name: $name) {
            name
            birthdate
        }
    }`

function App() {
    return (
        <MDBContainer className="App" fluid={true}>
            <MDBRow>
                <AllTogether/>
            </MDBRow>
            <ListRelations/>
        </MDBContainer>
    );
}

function ListRelations() {
    const [relation, setRelation] = useState({name: ""})
    const [allRelation, setAllRelation] = useState({
        parents: [],
        children: [],
        grandparents: [],
        siblings: [],
        cousins: []
    });
    const [search, {loading, data, error}] = useLazyQuery(GET_ALL_RELATIONS);

    if (loading) {
        console.log(error);
        console.log(loading);
    }

    function renderOutput() {
        let parents = [];
        let children = [];
        let grandparents = [];
        let cousins = [];
        let siblings = [];
        if (data) {
            if (data.parents.length !== 0) {
                data.parents.forEach(element => parents.push(element.name + " (" + element.birthdate + ")"));
            }
            if (data.children.length !== 0) {
                data.children.forEach(element => children.push(element.name + " (" + element.birthdate + ")"));
            }
            if (data.grandparents.length !== 0) {
                data.grandparents.forEach(element => grandparents.push(element.name + " (" + element.birthdate + ")"));
            }
            if (data.cousins.length !== 0) {
                data.cousins.forEach(element => cousins.push(element.name + " (" + element.birthdate + ")"));
            }
            if (data.siblings.length !== 0) {
                data.siblings.forEach(element => siblings.push(element.name + " (" + element.birthdate + ")"));
            }
        }
        setAllRelation({
            ...allRelation,
            parents: parents,
            children: children,
            grandparents: grandparents,
            siblings: siblings,
            cousins: cousins
        });
    }

    return (
        <MDBRow>
            <MDBCol sm={"2"}>
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        const result = e.target.elements.family_member.value;
                        search({variables: {name: result}})
                        renderOutput();
                    }}>
                    <p className="h4 text-center py-4">Wyszuka relacje danego członka rodziny</p>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Imie i nazwisko
                    </label>
                    <input
                        value={relation.name}
                        type="text"
                        id="defaultFormCardNameEx"
                        className="form-control"
                        name="family_member"
                        onChange={({target}) => setRelation({...relation, name: target.value})}
                    />
                    <div className="text-center py-4 mt-3">
                        <MDBBtn color="light-blue" className="mb-3" type="submit"
                                disabled={relation.name === ""}>
                            Wyszukaj
                        </MDBBtn>
                    </div>
                </form>
            </MDBCol>
            <MDBCol sm={"2"}>
                <br/>
                <br/>
                <br/>
                <p className="text-center">Rodzice</p>
                {allRelation.parents.map(function (item) {
                    return <p>{item}</p>;
                })}
            </MDBCol>
            <MDBCol sm={"2"}>
                <br/>
                <br/>
                <br/>
                <p className="text-center">Dzieci</p>
                {allRelation.children.map(function (item) {
                    return <p>{item}</p>;
                })}
            </MDBCol>
            <MDBCol sm={"2"}>
                <br/>
                <br/>
                <br/>
                <p className="text-center">Rodzeństwo</p>
                {allRelation.siblings.map(function (item) {
                    return <p>{item}</p>;
                })}
            </MDBCol>
            <MDBCol sm={"2"}>
                <br/>
                <br/>
                <br/>
                <p className="text-center">Dziadkowie</p>
                {allRelation.grandparents.map(function (item) {
                    return <p>{item}</p>;
                })}
            </MDBCol>
            <MDBCol sm={"2"}>
                <br/>
                <br/>
                <br/>
                <p className="text-center">Kuzyni</p>
                {allRelation.cousins.map(function (item) {
                    return <p>{item}</p>;
                })}
            </MDBCol>
        </MDBRow>
    );
}

function RelationsForm({onSubmitRelation}) {
    const [addRelation] = useMutation(ADD_RELATIONS);

    const [relation, setRelations] = useState({
        from_name: "",
        to_name: "",
        relationship_type: "PARENT",
    });
    return (
        <MDBCard>
            <MDBCardBody>
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        addRelation({
                            variables: {
                                from_name: relation.from_name,
                                to_name: relation.to_name,
                                relationship_type: relation.relationship_type
                            }, refetchQueries: {query: GET_ALL_PEOPLE_WITH_RELATIONS}
                        });
                        setRelations({...relation, from_name: "", to_name: "", relationship_type: ""});
                        onSubmitRelation();
                        onSubmitRelation();
                    }}
                    className="Form"
                >
                    <p className="h4 text-center py-4">Dodaj relacje między członkami rodziny</p>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Relacja od (imie i nazwisko)
                    </label>
                    <input
                        value={relation.from_name}
                        type="text"
                        id="defaultFormCardNameEx"
                        className="form-control"
                        onChange={({target}) => setRelations({...relation, from_name: target.value})}
                    />
                    <br/>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Do kogo
                    </label>
                    <input
                        value={relation.to_name}
                        className="form-control"
                        type="text"
                        id="defaultFormCardNameEx"
                        onChange={({target}) => setRelations({...relation, to_name: target.value})}
                    />
                    <br/>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Relacja
                    </label>
                    <select
                        className="browser-default custom-select"
                        onChange={({target}) => setRelations({...relation, relationship_type: target.value})}
                    >
                        <option>Wybierz relacje</option>
                        <option value="PARENT">Rodzic</option>
                        <option value="MARRIED">Współmałżonek</option>
                    </select>
                    <div className="text-center py-4 mt-3">
                        <MDBBtn color="light-blue" className="mb-3" type="submit"
                                disabled={relation.from_name === "" || relation.to_name === "" || relation.relationship_type === ""}>
                            Dodaj
                        </MDBBtn>
                    </div>
                </form>
            </MDBCardBody>
        </MDBCard>
    );
}

function PersonForm({onSubmitPerson}) {
    const [addPerson] = useMutation(ADD_PERSON);

    const [person, setPerson] = useState({
        name: "",
        birthdate: "",
        gender: "",
    });
    return (
        <MDBCard>
            <MDBCardBody>
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        addPerson({
                            variables: {name: person.name, birthdate: person.birthdate, gender: person.gender}
                        });
                        setPerson({...person, name: "", birthdate: "", gender: ""});
                        onSubmitPerson();
                        onSubmitPerson();
                    }}
                    className="Form"
                >
                    <p className="h4 text-center py-4">Dodaj członka rodziny</p>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Imię i nazwisko
                    </label>
                    <input
                        value={person.name}
                        type="text"
                        id="defaultFormCardNameEx"
                        className="form-control"
                        onChange={({target}) => setPerson({...person, name: target.value})}
                    />
                    <br/>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Data urodzenia
                    </label>
                    <input
                        value={person.birthdate}
                        className="form-control"
                        type="date"
                        id="example-date-input"
                        onChange={({target}) => setPerson({...person, birthdate: target.value})}
                    />
                    <br/>
                    <label
                        htmlFor="defaultFormCardNameEx"
                        className="grey-text font-weight-light"
                    >
                        Płeć
                    </label>
                    <select
                        className="browser-default custom-select"
                        onChange={({target}) => setPerson({...person, gender: target.value})}
                    >
                        <option>Wybierz płeć</option>
                        <option value="MALE">Mężczyzna</option>
                        <option value="FEMALE">Kobieta</option>
                    </select>
                    <div className="text-center py-4 mt-3">
                        <MDBBtn color="light-blue" className="mb-3" type="submit"
                                disabled={person.name === "" || person.birthdate === "" || person.gender === ""}>
                            Dodaj
                        </MDBBtn>
                    </div>
                </form>
            </MDBCardBody>
        </MDBCard>
    );
}

function getAllPeople(peoples) {
    let all_people = [];
    if (peoples.length !== 0) {
        peoples = peoples.slice().sort(function (a, b) {
            if (a.person.birthdate < b.person.birthdate) {
                return -1;
            }
            if (a.person.birthdate > b.person.birthdate) {
                return 1;
            }
            return 0;
        })
        let xCoord = 150;
        let yCoord = 30;
        let generationRoot = peoples[0];
        let generation = 0;
        let married = {};
        let parent = {};
        let spouse;
        peoples.forEach(function (data) {
            if (Math.abs(parseInt(data.person.birthdate.slice(0, 4)) - parseInt(generationRoot.person.birthdate.slice(0, 4))) > 15) {
                generation += 1;
                yCoord += 80;
                xCoord = 150 - generation * 40;
                generationRoot = data;
            }
            if (data.married_with.length !== 0) {
                spouse = data.married_with[0].name;
                if (data.person.name in married) {
                    xCoord = married[data.person.name] + 120;
                } else {
                    xCoord += 240;
                    married[spouse] = xCoord;
                }
            } else if (data.parents.length !== 0) {
                xCoord = parent[data.parents[0].name] - 60;
                parent[data.parents[0].name] += 40;
            } else {
                xCoord += 240;
            }
            parent[data.person.name] = xCoord;
            all_people.push({
                id: data.person.name,
                color: "lightGreen",
                birthdate: data.person.birthdate,
                gender: data.person.gender,
                svg: svgTable[data.person.gender],
                x: xCoord,
                y: yCoord,
                labelPosition: "top",
            })
        });
    }
    return all_people;
}

function getLinksPeople(peoples) {
    let links_people = []
    peoples.forEach(function (person) {
        // Add parents to person
        if (person.parents.length !== 0) {
            person.parents.map((parent) => (
                links_people.push({source: parent.name, target: person.person.name, label: "R"})
            ))
        }
        // Add spouse to person
        if (person.married_with.length !== 0) {
            person.married_with.map((spouse) => (
                links_people.push({source: spouse.name, target: person.person.name, label: "M"})
            ))
        }
    });
    return links_people;
}

function AllTogether() {
    const [search, {loading, data, error}] = useLazyQuery(GET_ALL_PEOPLE_WITH_RELATIONS, {fetchPolicy: "network-only"});
    const allNewPeople = (data && data.people_with_parents) ? data.people_with_parents : null;

    if (loading) {
        console.log(loading, error);
    }
    let defaultData = {
        nodes: [],
        links: []
    };
    if (allNewPeople) {
        defaultData = {
            nodes: getAllPeople(allNewPeople),
            links: getLinksPeople(allNewPeople)
        }
    }

    const [myConfig, setMyConfig] = useState(
        {
            staticGraph: false,
            height: 500,
            width: 1000,
            nodeHighlightBehavior: true,
            node: {
                color: "lightgreen",
                highlightStrokeColor: "blue",
                labelProperty: "id",
                size: 200
            },
            link: {
                highlightColor: "lightblue",
                labelProperty: "label",
                renderLabel: true
            },
        });


    const onClickNode = function (nodeId, node) {
        console.log(`Clicked ${nodeId} at position ${node.x}, ${node.y}`)
    };

    const onClickLink = function (source, target) {
        window.alert(`Clicked link between ${source} and ${target}`);
    };

    function refreshGraph() {
        search();
    }

    function setActive() {
        search();
        setMyConfig(myConfig => {
            return {...myConfig, staticGraph: false}
        });
    }

    function setStatic() {
        search();
        setMyConfig(myConfig => {
            return {...myConfig, staticGraph: true}
        });
    }

    return (
        <MDBContainer fluid={true}>
            <div className="d-flex justify-content-center">
                <MDBBtn color="light-green" onClick={() => setActive()}>Wyrenderuj aktywne drzewo genalogiczne</MDBBtn>
                <MDBBtn color="light-green" onClick={() => setStatic()}>Wyrenderuj statyczne drzewo
                    genalogiczne</MDBBtn>
            </div>
            <MDBRow>
                <MDBCol>
                    <PersonForm onSubmitPerson={refreshGraph}/>
                </MDBCol>
                <MDBCol>
                    <Graph
                        id="family1-tree-graph" // id is mandatory
                        data={defaultData}
                        config={myConfig}
                        onClickNode={onClickNode}
                        onClickLink={onClickLink}/>
                </MDBCol>
                <MDBCol>
                    <RelationsForm onSubmitRelation={refreshGraph}/>
                </MDBCol>
            </MDBRow>
        </MDBContainer>
    )
}


export default App;