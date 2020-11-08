import axios from "axios";
import React, {Component} from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Cookies from 'js-cookie';

import Header from "./components/Header";
import Rooms from "./components/Rooms";
import RoomList from "./components/RoomList";
import SignIn from "./components/SignIn";
import {NotFound} from "./components/NotFound";

axios.interceptors.request.use(function (config) {
    const token = Cookies.get("token");
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }

    return config;
});

class App extends Component {
	render() {
		return (
            <Router>
                <div>
                    <Header />
                    <Switch>
                        <Route exact path="/" component={RoomList} />
                        <Route path="/rooms" component={Rooms} />
                        <Route path="/sign-in" component={SignIn} />
                        <Route path={["*", "/404"]} component={NotFound} />
                    </Switch>
                </div>
            </Router>
		);
	}
}

export default App;
