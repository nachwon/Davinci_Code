import React from 'react';
import { bind } from 'decko';
import Block from './block';
import './main.css';

const ws = new WebSocket("ws://localhost:8000/feed/1");

class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            'message': '',
            'data_to_send': ''
        }
    }

    componentWillMount() {
        ws.onmessage = (message) => {
            console.log(message);
            this.setState({
                "message": message.data
            })
        }
    }

    @bind
    handleClick() {
        const message = {
            "action": "add_player",
            "body": this.state.data_to_send
        }
        
        ws.send(JSON.stringify(message))
    }

    @bind
    handleChange(e) {
        console.log(e.target.value)
        this.setState({
            "data_to_send": e.target.value
        })
    }

    @bind
    startGame(e) {
        const message = {
            "action": "start_game",
            "body": ""
        }
        ws.send(JSON.stringify(message))
    }

    @bind
    takeTurn(e) {
        const message = {
            "action": "take_turn",
            "body": {
                "from_player_id": 1,
                "to_player_id": 2,
                "target": 3,
                "guess": 1
            }
        }
        ws.send(JSON.stringify(message))
    }

    @bind
    pickStartingBlocks(e) {
        const message = {
            "action": "pick_starting",
            "body": {
                "player": this.state.data_to_send
            }
        }

        ws.send(JSON.stringify(message))
    }

    render() {
        return (
            <div>
                <input onChange={this.handleChange} />
                <button onClick={this.handleClick}>Test</button>
                <button onClick={this.startGame}>Start Game!!</button>
                <button onClick={this.pickStartingBlocks}>Pick starting blocks!</button>
                <button onClick={this.takeTurn}>Action!</button>
                <div>
                    {this.state.message}
                </div>
                <div className="game-board">
                    {
                        [0,1,2,3,4,5,6,7,8,9,10,11].map((value, index) => {
                            return (
                                <Block number={value} showing={true} />
                            )
                        })
                    }
                </div>
            </div>
        )
    }
}

export default Main