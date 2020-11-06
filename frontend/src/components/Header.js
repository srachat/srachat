import React from "react";

import Logo from "./Logo";
import {Link} from "react-router-dom";

const Header = (props) => {
    return (
        <div className="header">
            <Logo />
            <Link to="/rooms/">All rooms</Link>
            <Link to="/rooms/my/">My rooms</Link>
            <Link to="/rooms/create/">Create new room</Link>
            <Link to="/sign-in/">Sign In</Link>
            <Link to="/sign-up/">Sign Up</Link>
        </div>
    );
};

export default Header;
