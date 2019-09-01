import React from 'react';
import { Button, Dialog } from '@material-ui/core';
import { observer } from 'mobx-react';
import GuessModalStore from "../stores/modalStore";

@observer
class GuessModal extends React.Component {
    constructor(props) {
        super(props);
        this.store = new GuessModalStore();
    }

    render() {
        return (
            <div>
            <Button onClick={() => this.store.open = true}>Test</Button>
            <Dialog open={this.store.open} onClose={() => this.store.open = false}>
                <div>
                    Test
                </div>
            </Dialog>
        </div>
        )
    }
}

export default GuessModal;