import React from "react";
import {Route, Switch, useRouteMatch} from "react-router-dom";
import RoomList from "./RoomList";
import CreateRoom from "./CreateRoom";
import Room from "./Room";
import {NotFound} from "./NotFound";

const Rooms = () => {
    let { path, } = useRouteMatch();
    return (
        <Switch>
            <Route exact path={path} component={RoomList}/>
            <Route path={`${path}/create/`} component={CreateRoom}/>
            {/* Temp placeholder */}
            <Route path={`${path}/my/`} component={NotFound}/>
            <Route path={`${path}/:id`} component={Room} />
        </Switch>
    );
}

export default Rooms;