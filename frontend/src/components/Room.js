// @flow
import React, {Component} from "react";
import axios from "axios";
import Comments from "./Comments";
import Cookies from "js-cookie";


type RoomData = {
    id: number;
    title: string;
    created: string;
    creator: number;
    first_team_name: string;
    first_team_votes: number;
    second_team_name: string;
    second_team_votes: number;
    is_active: boolean;
    language: string;
    admins: Array;
}


class Room extends Component {
    constructor(props) {
		super(props);
		this.props = props;
		this.id = props.match.params.id;
		this.roomUrl = `/pidor/rooms/${this.id}/`;
		this.state = { userState: { isCreator: false, isParticipant: false } };
		this.currentUserId = parseInt(localStorage.getItem("userId")) || -1;

		this.deleteRoom = this.deleteRoom.bind(this);
		this.submitMessage = this.submitMessage.bind(this);
		this.updateCreator = this.updateCreator.bind(this);
		this.updateParticipant = this.updateParticipant.bind(this);
	}

	updateCreator() {
        this.setState({
                userState: {
                    isCreator: this.currentUserId === this.state.creator,
                    isParticipant: this.state.userState.isParticipant
                }
            })
    }

    updateParticipant(participantIds) {
        this.setState({
                userState: {
                    isCreator: this.state.userState.isCreator,
                    isParticipant: participantIds.includes(this.currentUserId)
                }
            })
    }

    componentDidMount() {
		axios
            .get(this.roomUrl)
            .then(res => {
                this.setState(res.data);
                this.updateCreator();
                return axios
                        .get(`${this.roomUrl}users/`)
                        .then(res => this.updateParticipant(res.data))
                        .catch(err => console.log(err.response.statusText))
            })
            .catch(err => this.props.history.push("/404"));
	}

	deleteRoom() {
        axios
            .delete(this.roomUrl)
            .then(res => this.props.history.push("/"))
            .catch(err => console.log(err.response.statusText));
    }

    submitMessage(event) {
        event.preventDefault();
        const body = new FormData(event.target).get("body");
        axios
            .post(`${this.roomUrl}comments/`, {"body": body})
            .then(() => event.target.reset())
            .catch(err => console.log(err.response.statusText));
    }

	render() {
        return (
            <div className="room-content">
                {/* Extract the header into the separate component */}
                <div className="room-header">
                    <h1>{this.state.title}</h1>
                    <RoomHeaderViews />
                    <RoomHeaderTeamVotes
                        teamName={this.state.first_team_name}
                        teamVotes={this.state.first_team_votes}
                    />
                    <RoomHeaderTeamVotes
                        teamName={this.state.second_team_name}
                        teamVotes={this.state.second_team_votes}
                    />
                    {this.state.userState.isCreator && <button className="room-delete" onClick={this.deleteRoom}>Delete room</button> }
                </div>
                <Comments roomUrl={this.roomUrl} />
            {/*  Extract the footer into the separate component  */}
            <div className="room-footer">
                {this.state.userState.isParticipant ? (
                    <form onSubmit={this.submitMessage}>
                        <input name="body" placeholder="Tell them your opinion"/>
                        <input type="submit" value="Send message" className="send-message" />
                    </form>
                ) : Cookies.get("token") && <span>You are not a participant</span>}
            </div>
            </div>
        );
    }
}

const RoomHeaderViews = () => {
    return <span>100500 viewers</span>;
};

const RoomHeaderTeamVotes = ({teamName, teamVotes}) => {
    return (
        <div className="team-votes">
            <span>{teamName}</span>
            <span>{teamVotes}</span>
        </div>
    );
};


export default Room;