import React, {Component} from "react";
import axios from "axios";
import Comment from "./Comments";
import Cookies from "js-cookie";
import ReconnectingWebSocket from "reconnecting-websocket";


class Room extends Component {
    constructor(props) {
		super(props);
		this.props = props;
		this.id = props.match.params.id;
		this.roomUrl = `/pidor/rooms/${this.id}/`;
		this.state = {
		    comments: [],
		    userState: { isCreator: false, isParticipant: false },
            firstRoomFilled: false, secondRoomFilled: false,
            websocket: undefined
        };
		this.currentUserId = parseInt(JSON.parse(localStorage.getItem("userdata"))?.userId) || -1;

		this.deleteRoom = this.deleteRoom.bind(this);
		this.fetchUsers = this.fetchUsers.bind(this);
		this.joinTeam = this.joinTeam.bind(this);
		this.submitMessage = this.submitMessage.bind(this);
		this.updateCreator = this.updateCreator.bind(this);
		this.updateParticipation = this.updateParticipation.bind(this);
	}

    constructWebSocket() {
        // This is WIP
        // Next patches will bring room join, comment deletion/update,
        // subchat separation, viewer count
        const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
        const ws = new ReconnectingWebSocket(`${ws_scheme}://${window.location.host}/ws${this.roomUrl}`);
        ws.onopen = () => { console.log("Successfully joined the room :)") }
        ws.onmessage = event => {
            const data = JSON.parse(event.data);
            if (data.type === "error") {
                alert(data.error_message)
            } else {
                this.setState({ comments: this.state.comments.concat(data.comments) });
            }
        }
        ws.onerror = error => { console.log(error) }
        ws.onclose = () => { console.log("Disconnected") }
        return ws;
    }

	updateCreator() {
        this.setState({
                userState: {
                    isCreator: this.currentUserId === this.state.creator,
                    isParticipant: this.state.userState.isParticipant
                }
            })
    }

    fetchUsers() {
        return axios
            .get(`${this.roomUrl}users/`)
            .then(res => this.updateParticipation(res.data))
            .catch(err => console.log(err.response.statusText))
    }

    updateParticipation(participantIds) {
        const allParticipants = Object.values(participantIds).flat();
        this.setState({
                userState: {
                    isCreator: this.state.userState.isCreator,
                    isParticipant: allParticipants.includes(this.currentUserId)
                },
                firstRoomFilled: participantIds["1"].length >= this.state.max_participants_in_team,
                secondRoomFilled: participantIds["2"].length >= this.state.max_participants_in_team,
            })
    }

    componentDidMount() {
		axios
            .get(this.roomUrl)
            .then(res => {
                this.setState(res.data);
                this.updateCreator();
                return this.fetchUsers();
            })
            .catch(err => this.props.history.push("/404"));
        this.setState({websocket: this.constructWebSocket()});
	}

    componentWillUnmount() {
        this.state.websocket && this.state.websocket.close();
        this.setState({ websocket: undefined });
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
        event.target.reset();
        this.state.websocket.send(JSON.stringify({"body": body}));
    }

    joinTeam(event) {
        event.preventDefault();
        const teamNumber = parseInt(event.target.id);
        axios
            .post(`${this.roomUrl}users/`, {"team_number": teamNumber})
            .then(() => this.fetchUsers())
            .catch(err => console.log(err));
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
                <div className="comments">
                    {this.state.comments.map(comment => <Comment key={comment.id} {...comment} />)}
                </div>
            {/*  TODO: Extract the footer into the separate component  */}
            <div className="room-footer">
                {this.state.userState.isParticipant ? (
                    <form onSubmit={this.submitMessage}>
                        <input name="body" placeholder="Tell them your opinion" required={true}/>
                        <input type="submit" value="Send message" className="send-message" />
                    </form>
                ) : Cookies.get("token") && (
                    <div className="team-join">
                        <button
                            onClick={this.joinTeam}
                            id={1}
                            disabled={this.state.firstRoomFilled}
                        >
                            Join {this.state.first_team_name}
                        </button>
                        <button
                            onClick={this.joinTeam}
                            id={2}
                            disabled={this.state.secondRoomFilled}
                        >
                            Join {this.state.second_team_name}
                        </button>
                    </div>
                )}
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