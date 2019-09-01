import React from 'react';
import { bind } from 'decko';
import Block from './block';
import './main.css';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';

const ws = new WebSocket("ws://localhost:8000/feed/1");

class Main extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            message: '',
            data_to_send: '',
            player_id: '',
            name: '',
            guess: '',
            showGuessModal: false
        }
    }

    componentWillMount() {
        ws.onmessage = (message) => {
            console.log(message);

            const loadedMessage = JSON.parse(message.data);

            if (loadedMessage.action === "add_player" && !this.state.player_id) {
                console.log(this.state.player_id);
                console.log("Adding player id!!")
                this.setState({
                    "player_id": loadedMessage.body.player_id,
                    "name": loadedMessage.body.name
                })
            } else {
                this.setState({
                    "message": message.data
                })
            }
        }
    }

    @bind
    addPlayer() {
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
                "player": this.state.data_to_send,
                "block_number": 1
            }
        }

        ws.send(JSON.stringify(message))
    }

    @bind
    pickBlock(block_index) {

        console.log('picking', this.state.player_id)
        const message = {
            "action": "pick_block",
            "body": {
                "player_id": this.state.player_id,
                "block_index": block_index
            }
        }
        console.log(message)

        this.sendMessage(message);
    }

    takeTurn(from_player_id, to_player_id, target, guess) {
        const message = {
            "action": "take_turn",
            "body": {
                "from_player_id": from_player_id,
                "to_player_id": to_player_id,
                "target": target,
                "guess": guess
            }
        }

        this.sendMessage(message);
    }

    @bind
    showGuessModal(from_player_id, to_player_id, target, guess) {
        console.log(this.state.showGuessModal);
        this.setState({
            showGuessModel: true,
        })
    }

    sendMessage(message) {
        ws.send(JSON.stringify(message));
    }

    renderRemainingBlocks(message) {
        let messageObj = {};
        if (message) {
            try {
                messageObj = JSON.parse(message)
            } catch(e) {
                messageObj = message
            }
        }
        
        if (messageObj.hasOwnProperty('remaining_blocks')) {
            return messageObj.remaining_blocks.map((value, index) => {
                return (
                    <Block 
                        onClick={this.pickBlock} 
                        key={index} 
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={false} 
                    />
                )
            }
        )}
    }

    renderYourBlocks(message) {
        let messageObj = {};
        if (message) {
            messageObj = JSON.parse(message)
        }
        
        if (messageObj.hasOwnProperty('player_1')) {
            return messageObj.player_1.deck.map((value, index) => {
                return (
                    <Block 
                        onClick={() => this.showGuessModal(2, 1, index, this.state.guess)} 
                        key={index} 
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={`player_${this.state.player_id}` === 'player_1'} 
                    />
                )
            }
        )}
    }

    renderMyBlocks(message) {
        let messageObj = {};
        if (message) {
            messageObj = JSON.parse(message)
        }

        if (messageObj.hasOwnProperty('player_2')) {
            return messageObj.player_2.deck.map((value, index) => {
                return (
                    <Block 
                        onClick={() => this.showGuessModal(1, 2, index, this.state.guess)} 
                        key={index} 
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={`player_${this.state.player_id}` === 'player_2'} 
                    />
                )
            }
        )}
    }

    render() {
        const { showGuessModal } = this.state;

        console.log(showGuessModal, 'modal!!')
        return (
            <div>
                <input onChange={this.handleChange} />
                {this.state.player_id ? null : <button onClick={this.addPlayer}>Add Player</button>}
                <button onClick={this.startGame}>Start Game!!</button>
                <button onClick={this.pickStartingBlocks}>Pick starting blocks!</button>
                <button onClick={this.takeTurn}>Action!</button>
                <div>
                    <span>My Name: {this.state.name}</span>
                    <span>ID: {this.state.player_id}</span>
                </div>
                
                <div className="game-board">
                    <div className={"game-board-opponent"}>
                        {this.renderYourBlocks(this.state.message)}
                    </div>
                    <div className={"game-board-remaining"}>
                        {this.renderRemainingBlocks(this.state.message)}
                    </div>
                    <div className={"game-board-mine"}>
                        {this.renderMyBlocks(this.state.message)}
                    </div>
                </div>

                <Button variant="outlined" onClick={() => this.setState({showGuessModal: true})}>Modal!</Button>

                <Dialog
                    open={showGuessModal}
                    onClose={() => this.setState({showGuessModal: false})}
                >
                    <div>test</div>
                </Dialog>
            </div>
        )
    }
}

export default Main