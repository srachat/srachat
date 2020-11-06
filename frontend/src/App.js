import React, {Component} from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Header from "./components/Header";
import Rooms from "./components/Rooms";
import RoomList from "./components/RoomList";

class App extends Component {
	render() {
		return (
            <Router>
                <div>
                    <Header />
                    <Switch>
                        <Route exact path="/" component={RoomList} />
                        <Route path="/rooms" component={Rooms} />
                    </Switch>
                </div>
            </Router>
		);
	}
}

export default App;
