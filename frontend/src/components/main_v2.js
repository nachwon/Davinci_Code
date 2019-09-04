import React from 'react';
import { Container, Snackbar, Avatar } from '@material-ui/core';
import GameBoard from '../components/board';
import PlayerStatus from '../components/playerStatus';
import { observer } from 'mobx-react';
import { bind } from 'decko';
import './main.css';
import MainStore from '../stores/mainStore';
import CustomizedSnackbars from './snackBarMessage';
import { gameStateEnum } from './enums';

@observer
class Main extends React.Component {
    constructor(props) {
        super(props);
        this.store = new MainStore();
        this.ws = new WebSocket("ws://localhost:8000/feed/1");
        this.ws.onmessage = (message) => this.store.handleMessage(message)
        this.store.ws = this.ws;
    }

    render() {
        return (
            <Container>
                <div>
                    <div>{`My ID: ${this.store.playerId}`}</div>
                    <div>{`Game State: ${this.store.gameState}`}</div>
                    <div>{`Action: ${this.store.action}`}</div>
                    <div>{`Turn: ${this.store.turn}`}</div>
                    <div>{this.store.playerId === this.store.turn ?
                        "My Turn" : "Not My Turn"
                    }</div>
                    <div>{`player state: ${this.store.playerState}`}</div>
                </div>
                {this.store.gameState === gameStateEnum.C ?
                    <PlayerStatus MainStore={this.store} />
                    :null}
                {this.store.gameState === gameStateEnum.I || this.store.gameState === gameStateEnum.P ?
                    <GameBoard MainStore={this.store} /> 
                    : null}
                {/* <Snackbar
                    open={this.store.showMessage}
                    autoHideDuration={3000}
                    variant={this.store.variant}
                    onClose={() => this.store.showMessage = false}
                    message={this.store.message}
                    anchorOrigin={{
                        vertical: 'bottom',
                        horizontal: 'left',
                      }}
                /> */}
                <CustomizedSnackbars 
                    open={this.store.showMessage}
                    message={this.store.message}
                    variant={this.store.variant}
                    onClose={() => this.store.showMessage = false}
                />
            </Container>
        )
    }
}

export default Main;