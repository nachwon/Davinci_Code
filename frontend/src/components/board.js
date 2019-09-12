import React from 'react';
import { Dialog, Radio, Button, FormControlLabel, DialogTitle, Zoom, Fab } from '@material-ui/core';
import { observer, inject } from "mobx-react";
import LoopIcon from '@material-ui/icons/Loop';
import "./board.css";
import { Block } from './block';

@inject('MainStore')
@observer
class GameBoard extends React.Component {
    constructor(props) {
        super(props);
        this.store = props.MainStore;
    }

    render() {
        console.log(this.store.action === 'place_joker')
        return (
            <div className="game-board">
                {['confirm_block', 'place_joker', 'reorder_joker'].includes(this.store.action) ?
                    <div className="confirm-block">
                        <Block 
                            onClick={this.store.confirmDraw} 
                            number={this.store.confirmBlock.number} 
                            color={this.store.confirmBlock.color} 
                            showing={true}
                        />
                        {this.store.action === 'confirm_block' ?
                            <Button className="confirm-block-button" onClick={this.store.confirmDraw}>Confirm</Button>
                            : null
                        }
                    </div> : null
                }

                <div className="game-board-opponent">
                    {this.store.renderOpponentBlocks}
                </div>
                <div className="game-board-remaining">
                    {this.store.renderRemainingBlocks}
                </div>
                <div className="game-board-mine">
                    {
                        this.store.action === 'place_joker' ? 
                            this.store.renderBlocksWithJokerPositioner : 
                            this.store.action === 'reorder_joker' ?
                                this.store.renderJokerReorder :
                                this.store.renderMyBlocks
                    }
                </div>

                {this.store.playerState === 'MG' ? 
                    <div className="yield-button">
                        <Zoom
                            onClick={this.store.yieldTurn}
                            unmountOnExit
                            variant="extended" 
                            color="secondary"
                            in={true}
                            style={{
                                transitionDelay: '500ms',
                            }}
                        >
                            <Fab>
                                <LoopIcon />
                                Yield Turn
                            </Fab>
                        </Zoom>
                    </div>:null}
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