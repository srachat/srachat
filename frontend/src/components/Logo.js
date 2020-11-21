import React from "react";
import {Link} from "react-router-dom";

const Logo = () => {
    return (
        <Link to={"/"}>
            <img src={process.env.REACT_APP_STATIC_FILES + "/SraChat.svg"} alt="logo" width="120px"/>
        </Link>
    );
};

export default Logo;