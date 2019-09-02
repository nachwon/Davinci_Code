import React from 'react';
import { Dialog, Radio, Button } from '@material-ui/core';
import { observer, inject } from "mobx-react";
import "./board.css";

@inject('MainStore')
@observer
class GameBoard extends React.Component {
    constructor(props) {
        super(props);
        this.store = props.MainStore;
    }

    render() {
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
                <Dialog open={this.store.openModal} onClose={() => this.store.openModal = false}>
                    <div className="guess-modal-wrapper">
                        {['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '-'].map((value, index) => {
                            return <Radio
                                key={index}
                                checked={this.store.guess === value}
                                onChange={this.store.handleGuessChange}
                                value={value}
                                name="radio-button-demo"
                            />
                        })}
                        <Button onClick={this.store.makeGuess}>Guess!</Button>
                    </div>
                </Dialog>
            </div>
        )
    }
}

export default GameBoard;