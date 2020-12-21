import React from "react";

import Tag from "./Tag"
import {Link} from "react-router-dom";

const RoomCardImage = ({url}) => {
    if (url === null) {
        url = process.env.REACT_APP_STATIC_FILES + "/default-image.png";
    }
    return <img alt="room-card-thumbnail" src={url} className="room-card-image" />
}

const RoomCardInfo = ({title, tags}) => {
    return (
        <div className="room-card-info">
            <h3 className="room-card-title">{title}</h3>
            {
                tags && tags.map(
                    tag => <Tag key={tag} title={tag} />
                )
            }
        </div>
    );
}

const RoomCard = ({id, title, tags, imgUrl}) => {
    return (
        <div className="room-card">
            <Link to={`/rooms/${id}`} >
                <RoomCardImage url={imgUrl} />
                <RoomCardInfo title={title} tags={tags} />
            </Link>
        </div>
    );
}

export default RoomCard;
