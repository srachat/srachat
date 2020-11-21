import React, {Component} from "react";
import axios from "axios";
import RoomCard from "./RoomCard";

class RoomList extends Component {
    constructor(props) {
		super(props);
		this.queryString = this.props.location.search;
		this.state = {
		    rooms: []
		};
	}

	componentDidMount() {
		axios
            .get(`/pidor/rooms/${this.queryString}`)
            .then(res => this.setState({ rooms: res.data }))
            .catch(err => console.log(err));
	}

	render() {
		return (
		    <div className="room-container">
                {
                    this.state.rooms.map(room =>
                        <RoomCard key={room.id} id={room.id} title={room.title} tags={room.tags} imgUrl={room.image}/>)
                }
            </div>
		);
	}
}

export default RoomList;