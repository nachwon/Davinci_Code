import React from 'react';
import { observer, inject } from 'mobx-react';
import { Typography, Paper, Button, Grid, Avatar } from '@material-ui/core';
import AddPlayerForm from './addPlayerForm';


@inject('MainStore')
@observer
class PlayerStatus extends React.Component {
    constructor(props) {
        super(props)
        this.store = props.MainStore;
    }

    renderPlayerList() {
        return this.store.players.map((value, index) => {
            return (
            <Avatar 
                className={value.name === this.store.playerName ? 'player-avatar player-avatar-me': 'player-avatar'} 
                key={index}
            >
                {value.name.slice(0, 2)}
            </Avatar>)
        })
    }

    render() {
        return (
            <div>
                {this.store.playerId ? 
                    <Paper className='player-status-container'>
                        <Typography variant="h5" component="h3">
                            {`Player ID: ${this.store.playerId}`}
                        </Typography>
                        <Typography component="p">
                            {`Player Name: ${this.store.playerName}`}
                        </Typography>
                        <Button onClick={(e) => this.store.startGame(this.ws)}>Start Game</Button>
                    </Paper>
                    :
                    <AddPlayerForm MainStore={this.store} />}
            <Grid container justify="center" alignItems="center">
                {this.renderPlayerList()}
            </Grid>
        </div>
        )
    }
}

export default PlayerStatus;