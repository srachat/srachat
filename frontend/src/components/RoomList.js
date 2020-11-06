import React, {Component} from "react";
import axios from "axios";
import RoomCard from "./RoomCard";

class RoomList extends Component {
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
                    this.state.rooms.map(room =>
                        <RoomCard id={room.id} title={room.title} tags={room.tags} imgUrl={room.image}/>)
                }
            </div>
		);
	}
}

export default RoomList;