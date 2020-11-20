import React, {Component} from "react";

class Comment extends Component {
    constructor({body, created, team_number, creator}) {
        super();
        const date = new Date(created);
        const hours = date.getUTCHours();
        const minutes = date.getMinutes() > 9 ? date.getMinutes() : `0${date.getMinutes()}`;
        this.state = {
            body: body,
            created: `${hours}:${minutes}`,
            team_number: team_number,
            creator: creator
        };
    }

    render() {
        return (
            <div className={`comment team-${this.state.team_number}`}>
                <span className="comment-body">{this.state.body}</span>
                <span className="comment-created">{this.state.created}</span>
            </div>
        );
    }
}

export default Comment;