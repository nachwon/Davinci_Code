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
    @observable gameState = 'CREATED'
    @observable remainingBlocks = []

    // Player State
    @observable players = [];
    @observable player_id = null;
    @observable player_name = null;

    // Deck State
    @observable myDeck = [];
    @observable opponentDeck = [];

    @action.bound
    handleMessage(message) {
        const response = JSON.parse(message.data);
        if (response.hasOwnProperty('message') && response.message) {
            this.message = response.message;
            this.showMessage = true;
        }

        if (response.action === 'update_game') {
            console.log(response, 'update');
            this.players = response.body.players;
            this.gameState = gameStateEnum[response.body.game_state];
            this.remainingBlocks = response.body.remaining_blocks;

            const me = this.players.filter((value) => {
                return value.name === this.player_name
            });
            const opponents = this.players.filter((value) => {
                return value.name !== this.player_name
            });

            if (me.length > 0 && opponents.length > 0) {
                this.myDeck = me[0].deck;
                this.opponentDeck = opponents[0].deck;
                console.log('decks', toJS(this.myDeck), toJS(this.opponentDeck))
            };
        }

        if (response.action === 'add_player') {
            this.handleAddPlayer(response)
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
    pickBlock(block_index) {
        const message = {
            "action": "pick_block",
            "body": {
                "player_id": this.player_id,
                "block_index": block_index
            }
        }
        this.sendMessage(message);
    }

    @action
    sendMessage(message) {
        this.ws.send(JSON.stringify(message));
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
                        onClick={() => this.showGuessModal(2, 1, index, this.state.guess)} 
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
        if (this.opponentDeck) {
            return this.opponentDeck.map((value, index) => {
                return (
                    <Block 
                        onClick={() => this.showGuessModal(2, 1, index, this.state.guess)} 
                        key={index} 
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={false} 
                    />
                )
            })
        }
    }
}

export default MainStore;

