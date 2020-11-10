import Cookies from "js-cookie";
import React from "react";
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

const Header = ({ updateUrlCallback }) => {
    return (
        <div className="header">
            <Logo />
            {
                HEADER_ROUTES.map(
                    headerRoute =>
                        <Link
                            to={headerRoute.url}
                            onClick={() => updateUrlCallback(headerRoute.url)}
                        >
                            {headerRoute.description}
                        </Link>
                )
            }
            <AuthSection />
        </div>
    );
};

const logOut = () => {
    Cookies.remove("token");
    localStorage.removeItem("userdata");
    window.location.reload(false);
}

const AuthSection = () => {
    const tokenCookie = Cookies.get("token");
    const username = JSON.parse(localStorage.getItem("userdata"))?.username;
    return (
        tokenCookie ? (
            <div className="authorized">
                <Link to="/" onClick={logOut}>Sign out</Link>
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
