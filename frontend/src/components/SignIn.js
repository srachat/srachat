import axios from "axios";
import Cookies from "js-cookie";
import React, {Component} from "react";

class SignIn extends Component {
    constructor(props) {
        super(props);

        this.history = props.history;

        this.handleLogIn = this.handleLogIn.bind(this);
        this.saveUserData = this.saveUserData.bind(this);
    }

    saveUserData(data) {
        localStorage.setItem("userId", data.pk);
        localStorage.setItem("username", data.username);
        localStorage.setItem("email", data.email);
        localStorage.setItem("firstName", data.first_name);
        localStorage.setItem("lastName", data.last_name);
    }

    handleLogIn(event) {
        event.preventDefault();
        const data = new FormData(event.target);
        const username = data.get("username");
        const password = data.get("password");
        axios
            .post("/pidor/rest-auth/login/", {username: username, password: password})
            .then(res => {
                Cookies.set("token", res.data.key);
                return axios
                    .get("/pidor/rest-auth/user/")
                    .then(res => {
                        this.saveUserData(res.data);
                        this.history.push("/");
                        window.location.reload();
                    })
                    .catch(err => {
                        console.log(err);
                        Cookies.remove("token");
                    });
            })
            .catch(err => console.log(err));
    }

    render() {
        return (
            <form onSubmit={this.handleLogIn}>
                <input name="username" placeholder="Username" required={true}/>
                <input name="password" placeholder="Password" type="password" required={true}/>
                <input type="submit" value="Sign in" />
            </form>
        )
    }
}

export default SignIn;