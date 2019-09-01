import React from 'react';
import { Dialog, Button } from '@material-ui/core';
import { observer, inject } from "mobx-react";
import BoardStore from "../stores/boardStore";
import GuessModal from "./guessModal";
import Block from "./block";
import { bind } from 'decko';

@inject('MainStore')
@observer
class GameBoard extends React.Component {
    constructor(props) {
        super(props);
        this.store = props.MainStore;
    }

    render() {
        console.log(this.store.remainingBlocks)
        return (
            <div className="game-board">
                <div className="game-board-opponent">
                    {this.store.renderYourBlocks}
                </div>
                <div className="game-board-remaining">
                    {this.store.renderRemainingBlocks}
                </div>
                <div className="game-board-mine">
                    {this.store.renderMyBlocks}
                </div>
            </div>
        )
    }
}

export default GameBoard;