import React, {Component} from "react";
import {CommentMenu} from "./Dropdown";

class Comments extends Component {
    constructor(props) {
        super(props);

        this.roomUrl = props.roomUrl;
        this.state = {
            comments: [],
            isParticipant: false,
            websocket: undefined,
            selectedMessagesIds: [],
            selectedMessagesToDelete: [],
            dropDown: { x: 0, y: 0 }
        }

		this.addToSelectedMessages = this.addToSelectedMessages.bind(this);
		this.removeFromSelectedMessaged = this.removeFromSelectedMessaged.bind(this);
		this.setDropDownCoord = this.setDropDownCoord.bind(this);
		this.deleteComments = this.deleteComments.bind(this);
		this.deleteCommentsCallback = this.deleteCommentsCallback.bind(this);
    }

    componentDidUpdate(prevProps: Readonly<P>, prevState: Readonly<S>, snapshot: SS) {
        if (prevProps.comments !== this.props.comments) {
            this.setState({ comments: this.props.comments })
        }
        if (prevProps.websocket !== this.props.websocket) {
            this.setState({ websocket: this.props.websocket })
        }
    }

    setParticipation(isParticipant) {
        this.setState({ isParticipant: isParticipant });
    }

    componentWillUnmount() {
        this.state.websocket && this.state.websocket.close();
        this.setState({ websocket: undefined });
    }

    addToSelectedMessages(id) {
        this.setState({ selectedMessagesIds: this.state.selectedMessagesIds.concat(id) });
        // +1 since this step somehow does not update the this.state.selectedMessagesIds immediately
        // some callback magic probably
        this.setState({ isManySelected: this.state.selectedMessagesIds.length + 1 > 1 });
    }

    removeFromSelectedMessaged(id) {
        this.setState({
            selectedMessagesIds: this.state.selectedMessagesIds.filter(messageId => messageId !== id)
        });
    }

    setDropDownCoord(coords) {
        this.setState({ dropDown: coords });
    }

    deleteComments() {
        this.state.websocket.send(JSON.stringify({
            "type": "delete_messages",
            "data": {"ids": this.state.selectedMessagesIds}
        }));
        this.setState({ selectedMessagesToDelete: this.state.selectedMessagesIds })
    }

    deleteCommentsCallback() {
        this.setState({
            comments: this.state.comments.filter(
                comment => !this.state.selectedMessagesToDelete.includes(comment.id)
            )
        });
        this.setState({ selectedMessagesToDelete: [] });
    }

    render() {
        return (
            <div className="comments">
                {
                    this.state.selectedMessagesIds?.length !== 0 &&
                    <CommentMenu
                        coords={this.state.dropDown}
                        actions={{
                            deleteComments: this.deleteComments
                        }}
                    />
                }
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