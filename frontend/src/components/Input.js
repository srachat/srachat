import axios from "axios";
import React, {Component} from "react";
import Select from 'react-select';

const FormInput = ({label, name, placeholder, required}) => {
    return (
        <div className="form-input">
            <label className="form-label">
                {label}
                <input name={name} placeholder={placeholder} required={required}/>
            </label>
        </div>
    );
}

class TagSelector extends Component{
    constructor({label, name}) {
        super();
        this.label = label;
        this.name = name;
        this.state = {
            tags: []
        }
    }

    componentDidMount() {
        axios
            .get("/pidor/tags/")
            .then(res => this.setState({tags: res.data.map(tag => {return {value: tag.id, label: tag.name}})}))
            .catch(err => console.log(err.response.statusText));
    }

    render() {
        return (
            <div className="tag-selector">
                <label className="form-label">
                    {this.label}
                    <Select isMulti options={this.state.tags} name={this.name} defaultValue={{value: 1, label: "Others"}}/>
                </label>
            </div>
        );
    }
}

export {FormInput, TagSelector}