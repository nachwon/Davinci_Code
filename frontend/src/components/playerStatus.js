import React from 'react';
import { Stepper, Step, StepLabel } from '@material-ui/core/';
import { EventSeat, Eject, Feedback } from '@material-ui/icons';
import { observer, inject } from 'mobx-react';
import { bind } from 'decko';
import './playerStatus.css';

@inject('MainStore')
@observer
class PlayerStatus extends React.Component {
    constructor(props) {
        super(props);
        this.store = props.MainStore;
        this.icons = {
            1: <EventSeat />,
            2: <Eject />,
            3: <Feedback />
        }
    }

    @bind
    renderIcon(props) {
        console.log(props);
        return(
            this.icons[props.icon]
        )
    }



    render() {
        return (
            <Stepper className='player-status-bar' activeStep={this.store.getActiveStep}>
                <Step>
                    <StepLabel StepIconComponent={this.renderIcon}>Wait for your turn</StepLabel>
                </Step>
                <Step>
                    <StepLabel StepIconComponent={this.renderIcon}>Draw a block</StepLabel>
                </Step>
                <Step>
                    <StepLabel StepIconComponent={this.renderIcon}>Make a guess</StepLabel>
                </Step>
            </Stepper>
        )
    }
}

export default PlayerStatus;