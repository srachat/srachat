import React, {Component} from "react";
import axios from "axios";
import Cookies from "js-cookie";
import {Bomb, SettingsIcon} from "./Icons";
import {DummyMenu, RoomDropdownMenu} from "./Dropdown";
import Comments from "./Comments";


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
            showDropdown: false
        };
		this.currentUserId = parseInt(JSON.parse(localStorage.getItem("userdata"))?.userId) || -1;

		this.commentsRef = React.createRef();

		this.deleteRoom = this.deleteRoom.bind(this);
		this.fetchUsers = this.fetchUsers.bind(this);
		this.joinTeam = this.joinTeam.bind(this);
		this.leaveTeam = this.leaveTeam.bind(this);
		this.updateParticipation = this.updateParticipation.bind(this);
		this.showMenu = this.showMenu.bind(this);
		this.closeMenu = this.closeMenu.bind(this);
		this.submitMessage = this.submitMessage.bind(this);
	}

    fetchUsers() {
        return axios
            .get(`${this.roomUrl}users/`)
            .then(res => this.updateParticipation(res.data))
            .catch(err => console.log(err))
    }

    updateParticipation(participantIds) {
        const allParticipants = Object.values(participantIds).flat();
        this.setState({
            userState: {
                isCreator: this.currentUserId === this.state.creator,
                isParticipant: allParticipants.includes(this.currentUserId)
            },
            firstRoomFilled: participantIds["1"].length >= this.state.max_participants_in_team,
            secondRoomFilled: participantIds["2"].length >= this.state.max_participants_in_team,
            firstRoomParticipants: participantIds["1"].length,
            secondRoomParticipants: participantIds["2"].length
        });
    }

    componentDidMount() {
		axios
            .get(this.roomUrl)
            .then(res => {
                this.setState(res.data);
                return this.fetchUsers();
            })
            .catch(err => console.log(err));
	}

	deleteRoom() {
        axios
            .delete(this.roomUrl)
            .then(res => this.props.history.push("/"))
            .catch(err => console.log(err.response.statusText));
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

    getCorrectRoomMenu() {
        if (this.state.userState.isCreator || this.state.userState.isParticipant) {
            return <RoomDropdownMenu
                isParticipant={this.state.userState.isParticipant}
                isCreator={this.state.userState.isCreator}
                actions={{
                    deleteRoomAction: this.deleteRoom,
                    leaveRoomAction: this.leaveTeam
                }}
                />
        } else {
            return <DummyMenu />;
        }
    }

    showMenu(event) {
        event.preventDefault();

        this.setState({ showDropdown: !this.state.showDropdown }, () => {
            document.addEventListener('click', this.closeMenu);
            event.stopPropagation();
        });
    }

    closeMenu(event) {
        this.setState({ showDropdown: false }, () => {
            document.removeEventListener('click', this.closeMenu);
        });
    }

    submitMessage(event) {
        event.preventDefault();
        const body = new FormData(event.target).get("body");
        event.target.reset();
        this.commentsRef.current.submitMessage(body);
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
                        className={`room-settings room-header-item ${this.state.showDropdown ? "open" : ""}`}
                        onClick={this.showMenu}
                    >
                        <SettingsIcon />
                    </div>
                    {this.state.showDropdown && this.getCorrectRoomMenu()}
                </div>
                <Comments roomUrl={this.roomUrl} ref={this.commentsRef} />
            {/*  TODO: Extract the footer into the separate component  */}
                {Cookies.get("token") &&
                <div className="room-footer">
                    { this.state.userState.isParticipant ? (
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