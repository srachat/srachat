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
    }

    componentDidMount() {
        const token = Cookies.get("token");
        if (token) {
            this.updateAuthCallback(true);
        }
    }

    render() {
       return (
            <div className="header">
                <Logo />
                {
                    HEADER_ROUTES.map(
                        headerRoute =>
                            <Link
                                to={headerRoute.url}
                                onClick={() => this.updateUrlCallback(headerRoute.url)}
                            >
                                {headerRoute.description}
                            </Link>
                    )
                }
                <AuthSection updateAuthCallback={this.updateAuthCallback} />
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
                <Link to="/" onClick={() => logOut(updateAuthCallback)}>Sign out</Link>
                <span className="header-username">{username}</span>
            </div>
        ) : (
            <div className="unauthorized">
                <Link to="/sign-in/">Sign In</Link>
                <Link to="/sign-up/">Sign Up</Link>
            </div>
        )
    );
}

export default Header;
