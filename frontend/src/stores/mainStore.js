import React from 'react';
import { observable, action, runInAction, computed, toJS } from 'mobx';
import { gameStateEnum } from '../components/enums';
import { Block, JokerPlacer } from "../components/block";


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
    @observable playerId = null;
    @observable playerName = null;
    @observable playerState = null;
    @observable player_1 = null;
    @observable player_2 = null;

    // Deck States
    @observable myDeck = [];
    @observable player2Deck = [];

    // GuessModal
    @observable openModal = false;
    @observable toPlayerId = null;
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
        } else if (response.action === 'update_game') {
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
                return value.name === this.playerName
            });
            const opponents = this.players.filter((value) => {
                return value.name !== this.playerName
            });

            if (me.length > 0 && opponents.length > 0) {
                this.myDeck = me[0].deck;
                this.playerState = me[0].state;
                this.player2Deck = opponents[0].deck;
            };
        } else if (response.action === 'guess_success') {
            this.showSnackBar(response.message, 'success');
        } else if (response.action === 'guess_fail') {
            this.showSnackBar(response.message, 'error');
        }
    }

    @action.bound
    handleAddPlayer(response) {
        if (response.body) {
            this.playerId = response.body.player_id
            this.playerName = response.body.name
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
            // If it is my turn
            if (this.playerId === this.turn) {
                // If the player state is in D
                if (this.playerState === 'D') {
                    const message = {
                        "action": "take_turn",
                        "body": {
                            "player_id": this.playerId,
                            "block_index": block_index
                        }
                    };
                    this.sendMessage(message);
                } else if (this.playerState === 'G') {
                    this.showSnackBar('You have to make a guess', 'warning')
                } else if (this.playerState === 'MG') {
                    this.showSnackBar('You cannot draw more. Either make a guess or yield turn.')
                }

            } else {
                this.showSnackBar('Not your turn', 'warning')
            }
        // If game is initiated
        } else {
            const message = {
                "action": "pick_block",
                "body": {
                    "player_id": this.playerId,
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
    showGuessModal(toPlayerId, target, isShowing) {
        if (this.gameState !== gameStateEnum.P || this.playerId !== this.turn || toPlayerId === this.playerId) {
            this.showSnackBar('Invalid operation!', 'error')
            return
        }

        if (isShowing) {
            this.showSnackBar("You've already guessed it!", 'info')
            return
        }

        if (this.playerState === 'D') {
            this.showSnackBar('Pick a block first!', 'warning')
            return
        }

        if (this.playerState === 'G' || this.playerState === 'MG') {
            if (this.playerId !== toPlayerId) {
                this.toPlayerId = toPlayerId;
                this.target = target;
                this.openModal = true;
            }
        }
    }

    @action.bound
    handleGuessChange(e) {
        this.guess = e.target.value;
    }

    @action.bound
    makeGuess(e) {
        const guess_message = {
            "action": "make_guess",
            "body": {
                "to_player_id": this.toPlayerId,
                "target": this.target,
                "guess": this.guess
            }
        }
        this.sendMessage(guess_message);
        this.openModal = false;
    }

    @action.bound
    yieldTurn(e) {
        const yield_message = {
            "action": "yield_turn",
            "body": ""
        }
        this.sendMessage(yield_message);
    }

    @action.bound
    placeJoker(position) {
        const message = {
            "action": "place_joker",
            "body": {
                "position": position
            }
        }
        this.sendMessage(message);
    }
    
    @computed get renderBlocksWithJokerPositioner() {

        const the_player = this.players[parseInt(this.playerId) - 1];

        if (the_player) {
            
            let children = [];
            the_player.deck.forEach((value, index) => {
                children.push(
                    <JokerPlacer 
                        key={`placer-${index}}`}
                        onClick={() => this.placeJoker(value.position)}
                    />
                );

                children.push(
                    <Block 
                        onClick={() => this.showGuessModal(this.playerId, index)} 
                        key={index}
                        index={index} 
                        number={value.number} 
                        color={value.color} 
                        showing={true} 
                    />
                )
            })

            children.push(
                <JokerPlacer 
                    key={1000}
                    onClick={() => this.placeJoker('last')}
                />
            );

            return children;
        }
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
            return index + 1 !== parseInt(this.playerId)
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

        const the_player = this.players[parseInt(this.playerId) - 1];

        if (the_player) {
            return the_player.deck.map((value, index) => {
                return (
                    <Block 
                        onClick={() => this.showGuessModal(this.playerId, index)} 
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

