import React from "react";

import Tag from "./Tag"

const RoomCardImage = ({url}) => {
    if (url === null) {
        url = "default-image.png"
    }
    return <img alt="room-card-image" src={url} className="room-card-image" />
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

const RoomCard = ({title, tags, imgUrl}) => {
    return (
        <div className="flex-item">
            <div className="room-card">
                <RoomCardImage url={imgUrl} />
                <RoomCardInfo title={title} tags={tags} />
            </div>
        </div>
    );
}

export default RoomCard;
