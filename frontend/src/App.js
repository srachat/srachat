import RoomCard from "./components/RoomCard"

import axios from "axios";
import React, {Component} from "react";

class App extends Component {
    constructor(props) {
		super(props);
		this.state = {
		rooms: []
		};
	}

	componentDidMount() {
		axios
		.get("/pidor/rooms/")
		.then(res => this.setState({ rooms: res.data }))
		.catch(err => console.log(err));
	}

	render() {
		return (
		<div className="container">
			{
			    this.state.rooms.map(room => <RoomCard title={room.title} tags={room.tags} imgUrl={room.image}/>)
			}
		</div>
		);
	}
}

export default App;
