import React from 'react';
import { Input, Button } from '@material-ui/core';
import { observer, inject } from 'mobx-react';
import { bind } from 'decko';


@inject('MainStore')
@observer
class AddPlayerForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            message: {}
        }
        this.store = props.MainStore;
        this.ws = this.store.ws;
        
    }

    @bind
    validateAndSend(e) {
        e.preventDefault();
        console.log(this.state.message);
        this.ws.send(JSON.stringify(this.state.message));
    }

    @bind
    handleChange(e) {
        this.setState({
            message: {
                action: 'add_player',
                body: {
                    name: e.target.value
                }
            }
        })
    }

    render() {
        return (
            <div className="add-player">
                <form className="add-player-form" onSubmit={this.validateAndSend}>
                    <Input placeholder="Player Name" onChange={this.handleChange}/>
                    <Button type='submit'>Join</Button>
                </form>
            </div>
        )
    }
}

export default AddPlayerForm;