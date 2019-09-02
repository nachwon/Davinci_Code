import React from 'react';
import { observable, action, runInAction, computed, toJS } from 'mobx';
import { gameStateEnum } from '../components/enums';
import Block from "../components/block";


class MainStore extends React.Component {
    @observable ws = null;

    @observable gameState = gameStateEnum.C;
    @observable showMessage = false;
    @observable message = '';

    // Game States
    @observable gameState = 'CREATED';
    @observable action = '';
    @observable remainingBlocks = [];
    @observable turn = null;

    // Player States
    @observable players = [];
    @observable player_id = null;
    @observable player_name = null;
    @observable player_state = null;

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
    handleMessage(message) {
        const response = JSON.parse(message.data);
        console.log('response', response);

        this.action = response.action;

        if (response.hasOwnProperty('message') && response.message) {
            this.message = response.message;
            this.showMessage = true;
        }

        if (response.action === 'add_player') {
            this.handleAddPlayer(response)
        }

        if (response.action === 'update_game') {
            console.log(response, 'update');
            this.players = response.body.players;
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
                    this.message = 'You have to make a guess';
                    this.showMessage = true;
                }

            } else {
                this.message = 'Not your turn'
                this.showMessage = true;
            }
        // If game is initiated
        } else {
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
    showGuessModal(to_player_id, target) {
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

    @computed get renderMyBlocks() {
        if (this.myDeck) {
            return this.myDeck.map((value, index) => {
                return (
                    <Block
                        onClick={() => this.showGuessModal(1, index)} 
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

    @computed get renderYourBlocks() {
        if (this.player2Deck) {
            return this.player2Deck.map((value, index) => {
                return (
                    <Block 
                        onClick={() => this.showGuessModal(2, index)} 
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
}

export default MainStore;

