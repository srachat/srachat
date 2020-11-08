import React, {Component} from "react";
import {FormInput, TagSelector} from "./Input";
import axios from "axios";

class CreateRoom extends Component {
    constructor(props) {
        super(props);
        this.history = props.history;
        this.state = {
            max_participants_in_team: 15,
            lifespan: "Day"
        }

        this.handleSubmit = this.handleSubmit.bind(this);
    }

    getData(event) {
        const formData = new FormData(event.target);
        const data = {};

        data["title"] = formData.get("title");
        const maxParticipants = formData.get("max_participants_in_team");
        if (maxParticipants) {
            data["max_participants_in_team"] = maxParticipants;
        }
        data["first_team_name"] = formData.get("first_team_name");
        data["second_team_name"] = formData.get("second_team_name");
        data["tags"] = formData.getAll("tags").map(tag => parseInt(tag));

		return data;
    }

    handleSubmit(event) {
        event.preventDefault();
        const data = this.getData(event);
        axios.post("/pidor/rooms/", data)
            .then(res => this.history.push(`/rooms/${res.data}`))
            .catch(err => console.log(err));
    }

    render() {
        return (
            <div className="create-room">
                <h1>Set up your room</h1>
                <form onSubmit={this.handleSubmit}>
                    <FormInput
                        label="Select a name for your room"
                        name="title"
                        placeholder="Room name"
                        required={true}
                    />
                    <TagSelector label="Add tags to your room so it can be easily found" name="tags"/>
                    <FormInput
                        label="How many participants can be in each team (max 50)"
                        name="max_participants_in_team"
                        placeholder="Default 15"
                        type="number"
                    />
                    {/*<FormDropDown*/}
                    {/*    label="Choose a life span of your room"*/}
                    {/*    name="lifespan"*/}
                    {/*    options={["Day", "Week", "Month", "Year"]}*/}
                    {/*/>*/}
                    <FormInput
                        label="Select a name for the red team"
                        name="first_team_name"
                        placeholder="Red team name"
                        required={true}
                    />
                    <FormInput
                        label="Select a name for the green team"
                        name="second_team_name"
                        placeholder="Green team name"
                        required={true}
                    />
                    <input type="submit" value="Create your room" />
                </form>
            </div>
        );
    }
}

export default CreateRoom;