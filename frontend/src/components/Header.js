import Cookies from "js-cookie";
import React, {Component} from "react";
import {Link} from "react-router-dom";

import Logo from "./Logo";

const HeaderRoute = (url, description) => {
    return { url: url, description: description }
}

const HEADER_ROUTES = [
    HeaderRoute("/rooms/", "All rooms"),
    HeaderRoute("/rooms/?filter=my", "My participation"),
    HeaderRoute("/rooms/create/", "Create new room")
]

class Header extends Component {
    constructor(props) {
        super(props);
        const { updateUrlCallback, updateAuthCallback, isAuth } = props;
        this.updateUrlCallback = updateUrlCallback;
        this.updateAuthCallback = updateAuthCallback;
        this.isAuth = isAuth;
        this.state = { isRoomZone: true }
    }

    componentDidMount() {
        const token = Cookies.get("token");
        if (token) {
            this.updateAuthCallback(true);
        }
    }

    checkIsActive(number) {
        return window.location.pathname + window.location.search === HEADER_ROUTES[number].url ? "active" : ""
    }

    render() {
       return (
            <div className="header">
                <div className="container">
                    <div className="logo" onClick={() => this.setState({isRoomZone: true})}>
                        <Logo />
                    </div>
                    <div className="participation-section">
                        <div className="rooms-section">
                            <Link
                                className={`participation-item ${this.checkIsActive(0)}`}
                                to={HEADER_ROUTES[0].url}
                                onClick={() => {
                                    this.setState(({isRoomZone: true}));
                                    return this.updateUrlCallback(HEADER_ROUTES[0].url);
                                }}
                            >
                                {HEADER_ROUTES[0].description}
                            </Link>
                            <Link
                                className={`participation-item ${this.checkIsActive(1)}`}
                                to={HEADER_ROUTES[1].url}
                                onClick={() => {
                                    this.setState(({isRoomZone: true}));
                                    return this.updateUrlCallback(HEADER_ROUTES[1].url);
                                }}
                            >
                                {HEADER_ROUTES[1].description}
                            </Link>
                        </div>
                        <Link
                            className="participation-item create-room"
                            to={HEADER_ROUTES[2].url}
                            onClick={() => this.updateUrlCallback(HEADER_ROUTES[2].url)}
                        >
                            {HEADER_ROUTES[2].description}
                        </Link>
                    </div>
                    <div className="auth-section">
                        <AuthSection updateAuthCallback={this.updateAuthCallback} />
                    </div>
                </div>
            </div>
        );
    }
}

const logOut = (updateAuthCallback) => {
    Cookies.remove("token");
    localStorage.removeItem("userdata");
    updateAuthCallback(false);
}

const AuthSection = ({ updateAuthCallback }) => {
    const tokenCookie = Cookies.get("token");
    const username = JSON.parse(localStorage.getItem("userdata"))?.username;
    return (
        tokenCookie ? (
            <div className="authorized">
                <span className="header-username">{username}</span>
                <Link to="/" onClick={() => logOut(updateAuthCallback)}>Sign out</Link>
            </div>
        ) : (
            <div className="unauthorized">
                <Link to="/sign-in/" className="unauthorized-item sign-in">Sign In</Link>
                <Link to="/sign-up/" className="unauthorized-item sign-up">Sign Up</Link>
            </div>
        )
    );
}

export default Header;
