import Cookies from "js-cookie";
import React from "react";
import {Link} from "react-router-dom";

import Logo from "./Logo";

const Header = (props) => {
    return (
        <div className="header">
            <Logo />
            <Link to="/rooms/">All rooms</Link>
            <Link to="/rooms/my/">My rooms</Link>
            <Link to="/rooms/create/">Create new room</Link>
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
