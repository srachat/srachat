import React, {Component} from "react";
import {CommentMenu} from "./Dropdown";
import ReconnectingWebSocket from "reconnecting-websocket";

class Comments extends Component {
    constructor(props) {
        super(props);

        this.props = props;

        this.roomUrl = props.roomUrl;
        this.state = {
            comments: [],
            isParticipant: false,
            websocket: undefined,
            selectedMessagesIds: [],
            dropDown: { x: 0, y: 0 }
        }

        this.constructWebSocket = this.constructWebSocket.bind(this);
		this.submitMessage = this.submitMessage.bind(this);
		this.addToSelectedMessages = this.addToSelectedMessages.bind(this);
		this.removeFromSelectedMessaged = this.removeFromSelectedMessaged.bind(this);
		this.setDropDownCoord = this.setDropDownCoord.bind(this);
    }

    setParticipation(isParticipant) {
        this.setState({ isParticipant: isParticipant });
    }

    componentDidMount() {
        if (this.state.websocket === undefined) {
            this.setState({
                websocket: this.constructWebSocket()
            });
        }
	}

    componentWillUnmount() {
        this.state.websocket && this.state.websocket.close();
        this.setState({ websocket: undefined });
    }

    constructWebSocket(loadMessagesOnConnect:boolean=true) {
        const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
        const ws = new ReconnectingWebSocket(`${ws_scheme}://${window.location.host}/ws${this.roomUrl}comments/`);
        ws.onopen = () => { console.log("Parsing messages") }
        ws.onmessage = event => {
            const data = JSON.parse(event.data);
            if (data.type === "error") {
                alert(data.error_message)
            } else if (data.type === "new_message") {
                if (loadMessagesOnConnect) {
                    this.setState({ comments: this.state.comments.concat(data.comments) });
                }
                window.scrollTo(0, document.querySelector(".comments")?.scrollHeight);
            }
        }
        ws.onerror = error => { console.log(error) }
        ws.onclose = () => { console.log("Disconnected") }
        return ws;
    }

    submitMessage(body) {
        this.state.websocket.send(JSON.stringify({"type": "new_message", "body": body}));
    }

    addToSelectedMessages(id) {
        this.setState({ selectedMessagesIds: this.state.selectedMessagesIds.concat(id) });
    }

    removeFromSelectedMessaged(id) {
        this.setState({
            selectedMessagesIds: this.state.selectedMessagesIds.filter(messageId => messageId !== id)
        });
    }

    setDropDownCoord(coords) {
        this.setState({ dropDown: coords });
    }

    render() {
        return (
            <div className="comments">
                {this.state.selectedMessagesIds?.length !== 0 && <CommentMenu coords={this.state.dropDown} />}
                {this.state.comments.map(comment =>
                    <Comment
                        key={comment.id}
                        addToSelectedMessages={this.addToSelectedMessages}
                        removeFromSelectedMessaged={this.removeFromSelectedMessaged}
                        setDropDownCoord={this.setDropDownCoord}
                        {...comment}
                    />)
                }
            </div>
        );
    }
}

class Comment extends Component {
    constructor({id, body, created, team_number, creator, addToSelectedMessages, removeFromSelectedMessaged, setDropDownCoord}) {
        super();
        const date = new Date(created);
        const hours = date.getUTCHours();
        const minutes = date.getMinutes() > 9 ? date.getMinutes() : `0${date.getMinutes()}`;
        this.state = {
            body: body,
            created: `${hours}:${minutes}`,
            team_number: team_number,
            creator: creator,
            selected: false
        };

        this.id = id;

        this.addToSelectedMessages = addToSelectedMessages;
        this.removeFromSelectedMessaged = removeFromSelectedMessaged;
        this.setDropDownCoord = setDropDownCoord;
        this.handleContextMenu = this.handleContextMenu.bind(this);
        this.selectComment = this.selectComment.bind(this);
        this.unSelectComment = this.unSelectComment.bind(this);
    }

    handleContextMenu(event) {
        event.preventDefault();
        event.stopPropagation();

        this.setDropDownCoord({ x: event.pageX + 5, y: event.pageY + 5 })

        const target = event.target;
        if (target.classList.contains("comment")) {
            if (this.state.selected) {
                this.unSelectComment(target);
            } else {
                this.selectComment(target);
            }
        }

        document.addEventListener("click", () => {this.unSelectComment(target)});
        document.addEventListener("contextmenu", () => {this.unSelectComment(target)});
    }

    selectComment(target) {
        this.addToSelectedMessages(this.id);
        this.setState({ selected: true });
        target.style.background = "#F54B2A";
    }

    unSelectComment(target) {
        this.removeFromSelectedMessaged(this.id);
        this.setState({ selected: false })
        target.style.background = "";
    }

    render() {
        return (
            <div className={`comment team-${this.state.team_number}`} onContextMenu={this.handleContextMenu}>
                <span className="comment-body">{this.state.body}</span>
                <span className="comment-created">{this.state.created}</span>
            </div>
        );
    }
}

export default Comments;