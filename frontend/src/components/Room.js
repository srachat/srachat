import React, {Component} from "react";
import {useParams} from "react-router-dom";
import axios from "axios";

class Room extends Component {
    constructor(props) {
		super(props);
		this.id = props.match.params.id;
		this.state = {};
	}

	componentDidMount() {
		axios
            .get(`/pidor/rooms/${this.id}`)
            .then(res => this.setState(res.data))
            .catch(err => console.log(err));
	}

	render() {
        console.log(this.state)
        return (
            <h1>{this.state.title}</h1>
        )
    }
}

export default Room;