import axios from "axios";
import React, {Component} from "react";

class Comments extends Component {
    constructor({roomUrl}) {
        super({roomUrl});
        this.roomUrl = roomUrl;
        this.state = {
            comments: []
        }
    }

    componentDidMount() {
        axios
            .get(`${this.roomUrl}comments`)
            .then(res => this.setState({comments: res.data}))
            .catch(err => console.log(err.response.statusText));
    }

    render() {
        return (
            <div className="comments">
                {this.state.comments.map(comment => <Comment {...comment} />)}
            </div>
        );
    }
}

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

export default Comments;