import React from 'react';
import { Dialog, Radio, Button, FormControlLabel, DialogTitle } from '@material-ui/core';
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
                    {this.store.renderOpponentBlocks}
                </div>
                <div className="game-board-remaining">
                    {this.store.renderRemainingBlocks}
                </div>
                <div className="game-board-mine">
                    {this.store.renderMyBlocks}
                </div>
                <Dialog open={this.store.openModal} onClose={() => this.store.openModal = false}>
                    <DialogTitle className="guess-modal-title">Guess the number!</DialogTitle>
                    <div className="guess-modal-wrapper">
                        {['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '-'].map((value, index) => {
                            return <FormControlLabel
                                value={value}
                                key={index}
                                control={<Radio checked={this.store.guess === value}/>}
                                onChange={this.store.handleGuessChange}
                                label={value}
                                labelPlacement="bottom"
                            />
                        })}
                        <div className="guess-modal-buttons">
                            <Button color="primary" onClick={this.store.makeGuess}>Guess</Button>
                            <Button color="secondary" onClick={() => this.store.openModal = false}>Cancel</Button>
                        </div>
                        
                    </div>
                </Dialog>
            </div>
        )
    }
}

export default GameBoard;