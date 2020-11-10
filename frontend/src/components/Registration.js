import axios from "axios";
import Cookies from "js-cookie";
import React, {Component} from "react";

class Auth extends Component {
    constructor(props) {
        super(props);

        this.history = props.history;

        this.buttonText = props.buttonText;
        this.url = props.url;

        this.prepareForm = this.prepareForm.bind(this);
        this.handleAuth = this.handleAuth.bind(this);
        this.getPostData = this.getPostData.bind(this);
        this.saveUserData = this.saveUserData.bind(this);
    }

    getPostData(formData) {}

    saveUserData(data) {
        localStorage.setItem("userdata", JSON.stringify(
            {
                userId: data.pk,
                username: data.username,
                email: data.email,
                firstName: data.first_name,
                lastName: data.last_name
            }
        ));
    }

    handleAuth(event) {
        event.preventDefault();
        const data = this.getPostData(new FormData(event.target));
        axios
            .post(`/pidor/rest-auth/${this.url}/`, data)
            .then(res => {
                console.log(this.history);
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
                        localStorage.removeItem("userdata");
                    });
            })
            .catch(err => console.log(err));
    }

    prepareForm() {}

    render() {
        return (
            <form onSubmit={this.handleAuth}>
                {this.prepareForm()}
                <input type="submit" value={this.buttonText} />
            </form>
        )
    }
}

class SignIn extends Auth {
    getPostData(formData) {
        const username = formData.get("username");
        const password = formData.get("password");
        return {username: username, password: password};
    }

    prepareForm() {
        return (
            <div className="form-sign-in">
                <input name="username" placeholder="Username" required={true}/>
                <input name="password" placeholder="Password" type="password" required={true}/>
            </div>
            );
    }
}

class SignUp extends Auth {
    getPostData(formData) {
        const email = formData.get("email") || "";
        const username = formData.get("username");
        const password = formData.get("password");
        return {
            username: username,
            password1: password,
            password2: password,
            ...(email && {email: email})
        };
    }

    prepareForm() {
        return (
            <div className="form-sign-in">
                <input name="username" placeholder="Username" required={true}/>
                <input name="email" placeholder="Email" type="email"/>
                <input name="password" placeholder="Password" type="password" required={true}/>
            </div>
            );
    }
}

export {SignIn, SignUp};
