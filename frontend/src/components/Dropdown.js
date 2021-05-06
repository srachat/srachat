import React from "react";

const DropdownMenu = ({options, name, coords}) => {
    const style = coords ? {left: coords.x, top: coords.y, width: "300px"} : {};
    return (
        <div className={`dropdown-menu-wrapper ${name}`} style={style}>
            {
                options.map(
                    ({name, action, className}) => (
                        <div key={className} className={`dropdown-menu-item ${className}`} onClick={action}>
                            {name}
                        </div>
                    )
                )
            }
        </div>
    )
}

export const RoomDropdownMenu = ({isParticipant, isCreator, actions}) => {
    const options = [];
    isParticipant && options.push(...[
                {name: "Leave the team", action: actions.leaveRoomAction, className: "leave-the-room"}
            ])
    isCreator && options.push(...[
                {name: "Ban user", action: actions.banUserAction, className: "ban-user"},
                {name: "Change room info", action: actions.changeRoomAction, className: "change-room-info"},
                {name: "Delete room", action: actions.deleteRoomAction, className: "delete-room delete"},
            ])

    return (
        <DropdownMenu
            options={options}
            name="edit-room-dropdown"
        />
    );

}

export const DummyMenu = () => {
    return (
        <DropdownMenu
            options={[
                {name: "No menu", action: () => alert("I told you that there is no menu!"), className: "no-menu"}
            ]}
            name="edit-room-dropdown"
        />
    )
}

export const CommentMenu = ({coords, actions}) => {
    const options = [
        {name: "Delete", action: actions.deleteComments, className: "delete-comment delete"},
    ]
    return (
        <DropdownMenu
            options={options}
            name="edit-room-dropdown"
            coords={coords}
        />
    )
}
