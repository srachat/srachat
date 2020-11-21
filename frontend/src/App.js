import axios from "axios";
import React, {useState} from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";
import Cookies from 'js-cookie';

import Header from "./components/Header";
import Rooms from "./components/Rooms";
import RoomList from "./components/RoomList";
import {SignIn, SignUp} from "./components/Registration";
import {NotFound} from "./components/NotFound";

axios.interceptors.request.use(function (config) {
    const token = Cookies.get("token");
    if (token) {
        config.headers.Authorization = `Token ${token}`;
    }

    return config;
});

const App = () => {
    const [ prevUrl, setPrevUrl ] = useState("");
    const [ isAuth, setAuth ] = useState(false);

	return (
        <Router>
            <div>
                <Header updateUrlCallback={setPrevUrl} updateAuthCallback={setAuth} isAuth={isAuth} />
                <div className="container main">
                    <Switch>
                        <Route exact path="/" component={RoomList} />
                        <Route path="/rooms" component={(props) => <Rooms {...props} prevUrl={prevUrl} />} />
                        <Route
                            path="/sign-in"
                            component={
                                props =>
                                    <SignIn
                                        {...props}
                                        buttonText="Sign in"
                                        url="login"
                                        updateAuthCallback={setAuth}
                                    />
                            }
                        />
                        <Route
                            path="/sign-up"
                            component={
                                props =>
                                    <SignUp
                                        {...props}
                                        buttonText="Sign up"
                                        url="registration"
                                        updateAuthCallback={setAuth}
                                    />
                            }
                        />
                        <Route path={["*", "/404"]} component={NotFound} />
                    </Switch>
                </div>
            </div>
        </Router>
    );
}

export default App;
