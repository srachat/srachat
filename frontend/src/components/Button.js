import React from "react";

const OutlinedButton = ({link, text}) => {
    return (
        <form action={link}>
            <input type="submit" value={text} />
        </form>

    );
};

export default OutlinedButton;
