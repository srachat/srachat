import React from "react";

const DropdownMenu = ({options, name}) => {
    return (
        <div className={`dropdown-menu-wrapper ${name}`}>
            {
                options.map(
                    ({name, action, className}) => (
                        <div className={`dropdown-menu-item ${className}`} onClick={action}>
                            {name}
                        </div>
                    )
                )
            }
        </div>
    )
}

export const EditRoomDropdownMenu = ({deleteRoomAction, changeRoomAction, banUserAction}) => {
    return (
        <DropdownMenu
            options={[
                {name: "Ban user", action: banUserAction, className: "ban-user"},
                {name: "Change room info", action: changeRoomAction, className: "change-room-info"},
                {name: "Delete room", action: deleteRoomAction, className: "delete-room"},
            ]}
            name="edit-room-dropdown"
        />
    );
}

export const ParticipantDropdownMenu = ({leaveRoomAction}) => {
    return (
        <DropdownMenu
            options={[
                {name: "Leave the room", action: leaveRoomAction, className: "leave-the-room"}
            ]}
            name="edit-room-dropdown"
        />
    )
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
