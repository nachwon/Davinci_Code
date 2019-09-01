import React from 'react';
import { observable } from 'mobx';


class GuessModalStore extends React.Component {
    @observable open = false
}

export default GuessModalStore;