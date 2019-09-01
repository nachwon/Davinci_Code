import React from 'react';
import { observable, action } from 'mobx';


class BoardStore extends React.Component {
    @observable myDeck = []
    @observable opponentDeck = []
    @observable remainingBlocks = []
    @observable showGuessModal = false
}

export default BoardStore;