import React, {Component} from "react";
import axios from "axios";
import Comment from "./Comments";
import Cookies from "js-cookie";
import ReconnectingWebSocket from "reconnecting-websocket";
import {Bomb, SettingsIcon} from "./Icons";
import {DummyMenu, EditRoomDropdownMenu, ParticipantDropdownMenu} from "./Dropdown";


class Room extends Component {
    constructor(props) {
		super(props);
		this.props = props;
		this.id = props.match.params.id;
		this.roomUrl = `/pidor/rooms/${this.id}/`;
		this.state = {
		    comments: [],
		    userState: { isCreator: false, isParticipant: false },
            firstRoomParticipants: 0, secondRoomParticipants: 0,
            firstRoomFilled: false, secondRoomFilled: false,
            websocket: undefined,
            roomMenuOpen: false
        };
		this.currentUserId = parseInt(JSON.parse(localStorage.getItem("userdata"))?.userId) || -1;

		this.deleteRoom = this.deleteRoom.bind(this);
		this.fetchUsers = this.fetchUsers.bind(this);
		this.joinTeam = this.joinTeam.bind(this);
		this.leaveTeam = this.leaveTeam.bind(this);
		this.submitMessage = this.submitMessage.bind(this);
		this.updateCreator = this.updateCreator.bind(this);
		this.updateParticipation = this.updateParticipation.bind(this);
	}

    constructWebSocket(loadMessagesOnConnect:boolean=true) {
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
                if (loadMessagesOnConnect) {
                    this.setState({ comments: this.state.comments.concat(data.comments) });
                }
                window.scrollTo(0, document.querySelector(".comments").scrollHeight);
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
            firstRoomParticipants: participantIds["1"].length,
            secondRoomParticipants: participantIds["2"].length
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

    leaveTeam(event) {
        event.preventDefault();
        axios
            .delete(`${this.roomUrl}users/`)
            .then(() => this.fetchUsers())
            .catch(err => console.log(err));
    }

    getCorrectMenu() {
        if (this.state.userState.isCreator) {
            return <EditRoomDropdownMenu deleteRoomAction={this.deleteRoom} />;
        } else if (this.state.userState.isParticipant) {
            return <ParticipantDropdownMenu leaveRoomAction={this.leaveTeam} />
        } else {
            return <DummyMenu />;
        }
    }

	render() {
        return (
            <div className="room-content">
                <div className="room-bg"/>
                {/* Extract the header into the separate component */}
                <div className="room-header">
                    <div className="room-title room-header-item">
                        <h2>{this.state.title}</h2>
                    </div>
                    <div className="room-views room-header-item">
                        <img src={process.env.REACT_APP_STATIC_FILES + "/views.svg"} alt="views" width="16px"/>
                        <h2>100</h2>
                        <span>viewers</span>
                    </div>
                    <div className="room-votes room-header-item">
                        <span className="room-votes-label">Pick a favourite:</span>
                        <div className="room-vote-items">
                            <RoomHeaderTeamVotes
                                teamName={this.state.first_team_name}
                                teamVotes={this.state.first_team_votes}
                                teamNumber="1"
                            />
                            <div className="room-vote-switch">Switch</div>
                            <RoomHeaderTeamVotes
                                teamName={this.state.second_team_name}
                                teamVotes={this.state.second_team_votes}
                                teamNumber="2"
                            />
                        </div>
                    </div>
                    <div
                        className={`room-settings room-header-item ${this.state.roomMenuOpen ? "open" : ""}`}
                        onClick={() => { this.setState({roomMenuOpen: !this.state.roomMenuOpen}) }}
                    >
                        <SettingsIcon />
                    </div>
                    {this.state.roomMenuOpen && this.getCorrectMenu()}
                </div>
                <div className="comments">
                    {this.state.comments.map(comment => <Comment key={comment.id} {...comment} />)}
                </div>
            {/*  TODO: Extract the footer into the separate component  */}
                {Cookies.get("token") &&
                <div className="room-footer">
                    {this.state.userState.isParticipant ? (
                        <form onSubmit={this.submitMessage} className="message" autoComplete="off">
                            <input name="body" placeholder="Tell them your opinion" required={true} className="send-message-text"/>
                            <button value="Send message" className="send-message-button">
                                <Bomb />
                            </button>
                        </form>
                    ) : (
                        <div className="team-join">
                            <div className="team-join-text">
                                <h2>You are a viewer</h2>
                                {
                                    this.state.firstRoomFilled && this.state.secondRoomFilled ?
                                        (
                                            <p>
                                                <span>Snap! </span>Both teams are already full
                                            </p>
                                    ) : (
                                            <p>
                                                <span>Join </span>a team to start bombing
                                            </p>
                                        )
                                }
                            </div>
                            <button
                                onClick={this.joinTeam}
                                id={1}
                                disabled={this.state.firstRoomFilled}
                                className="join-button team-1"
                            >
                                <span className="join-team-cta">
                                    Join <span className="join-team-name">{this.state.first_team_name}</span>
                                </span>
                                <span className="join-team-count">
                                    {this.state.firstRoomParticipants || 0} / {this.state.max_participants_in_team}
                                </span>
                            </button>
                            <button
                                onClick={this.joinTeam}
                                id={2}
                                disabled={this.state.secondRoomFilled}
                                className="join-button team-2"
                            >
                                <span className="join-team-cta">
                                    Join <span className="join-team-name">{this.state.second_team_name}</span>
                                </span>
                                <span className="join-team-count">
                                    {this.state.secondRoomParticipants || 0} / {this.state.max_participants_in_team}
                                </span>
                            </button>
                        </div>
                    )}
                </div>
                }
            </div>
        );
    }
}

const RoomHeaderTeamVotes = ({teamName, teamVotes, teamNumber}) => {
    return (
        <div className={`team-votes team-${teamNumber}`}>
            <span className="team-votes-name">{teamName}</span>
            <span className="team-votes-number">{teamVotes}</span>
        </div>
    );
};


export default Room;