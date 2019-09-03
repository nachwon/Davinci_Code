import React from 'react';
import { observable, action, runInAction, computed, toJS } from 'mobx';
import { gameStateEnum } from '../components/enums';
import Block from "../components/block";


class MainStore extends React.Component {
    @observable ws = null;

    // Snackbar messages
    @observable variant = 'info';
    @observable showMessage = false;
    @observable message = '';

    // Game States
    @observable gameState = gameStateEnum.C;
    @observable action = '';
    @observable remainingBlocks = [];
    @observable turn = null;

    // Player States
    @observable players = [];
    @observable player_id = null;
    @observable player_name = null;
    @observable player_state = null;
    @observable player_1 = null;
    @observable player_2 = null;

    // Deck States
    @observable myDeck = [];
    @observable player2Deck = [];

    // GuessModal
    @observable openModal = false;
    @observable to_player_id = null;
    @observable target = null;
    @observable guess = null;

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    @action.bound
    showSnackBar(message, variant='info') {
        this.variant = variant;
        this.message = message;
        this.showMessage = true;
    }

    @action.bound
    handleMessage(message) {
        const response = JSON.parse(message.data);
        console.log('response', response);

        this.action = response.action;

        if (response.hasOwnProperty('message') && response.message) {
            this.showSnackBar(response.message)
        }

        if (response.action === 'add_player') {
            this.handleAddPlayer(response)
        }

        if (response.action === 'update_game') {
            console.log(response, 'update');
            this.players = response.body.players;
            this.player_1 = response.body.player_1
            this.player_2 = response.body.player_2
            this.gameState = gameStateEnum[response.body.game_state];
            this.remainingBlocks = response.body.remaining_blocks;

            if (response.body.game_state === 'P') {
                this.turn = response.body.turn;
            }

            const me = this.players.filter((value) => {
                return value.name === this.player_name
            });
            const opponents = this.players.filter((value) => {
                return value.name !== this.player_name
            });

            if (me.length > 0 && opponents.length > 0) {
                this.myDeck = me[0].deck;
                this.player_state = me[0].state;
                this.player2Deck = opponents[0].deck;
            };
        }
    }

    @action.bound
    handleAddPlayer(response) {
        if (response.body) {
            this.player_id = response.body.player_id
            this.player_name = response.body.name
        }
    }

    @action
    setGameState(gameState) {
        this.gameState = gameStateEnum[gameState]
    };

    @action.bound
    startGame() {
        const message = {
            "action": "start_game",
            "body": ""
        }
        this.ws.send(JSON.stringify(message))
    }

    @action.bound
    async pickBlock(block_index) {
        // If game is playing
        if (this.gameState === gameStateEnum.P) {
            if (this.player_id === this.turn) {
                if (this.player_state === 'D') {
                    const message = {
                        "action": "take_turn",
                        "body": {
                            "player_id": this.player_id,
                            "block_index": block_index
                        }
                    };
                    this.sendMessage(message);
                } else if (this.player_state === 'G') {
                    this.showSnackBar('You have to make a guess', 'warning')
                }

            } else {
                this.showSnackBar('Not your turn', 'warning')
            }
        // If game is initiated
        } else {
            console.log("initiated, Pick block", this.player_id);
            const message = {
                "action": "pick_block",
                "body": {
                    "player_id": this.player_id,
                    "block_index": block_index
                }
            }
            this.sendMessage(message);
        }
        
    }

    @action
    sendMessage(message) {
        this.ws.send(JSON.stringify(message));
    }

    @action.bound
    showGuessModal(to_player_id, target, isShowing) {
        if (this.gameState !== gameStateEnum.P || this.player_id !== this.turn || to_player_id === this.player_id) {
            this.showSnackBar('Invalid operation!', 'info')
            return
        }

        if (isShowing) {
            this.showSnackBar("You've already guessed it!", 'info')
            return
        }

        if (this.player_state !== 'G') {
            this.showSnackBar('Pick a block first!', 'warning')
            return
        }
        if (this.player_id !== to_player_id) {
            this.to_player_id = to_player_id;
            this.target = target;
            this.openModal = true;
        }
    }

    @action.bound
    handleGuessChange(e) {
        this.guess = e.target.value;
    }

    @action.bound
    makeGuess(e) {
        const guess_message = {
            "to_player_id": this.to_player_id,
            "target": this.target,
            "guess": this.guess
        }
        this.sendMessage(guess_message);
        this.openModal = false;
    }

    @computed get renderRemainingBlocks() {
            return this.remainingBlocks.map((value, index) => {
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
        )
    }

    @computed get renderOpponentBlocks() {
        
        const the_opponents = this.players.filter((value, index) => {
            return index + 1 !== parseInt(this.player_id)
        });
        console.log('opponents', the_opponents)
        const the_opponent = the_opponents[0];

        if (the_opponent) {
            return the_opponent.deck.map((value, index) => {
                return (
                    <Block
                        onClick={() => this.showGuessModal(the_opponent.turn_id, index, value.showing)} 
                        key={index} 
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={value.showing} 
                    />
                )
            })
        }
    }

    @computed get renderMyBlocks() {

        const the_player = this.players[parseInt(this.player_id) - 1];

        if (the_player) {
            return the_player.deck.map((value, index) => {
                return (
                    <Block 
                        onClick={() => this.showGuessModal(this.player_id, index)} 
                        key={index}
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={true} 
                    />
                )
            })
        }
    }
}

export default MainStore;

