import React from 'react';
import './block.css';


class Block extends React.Component {
    constructor(props) {
        super(props)

    }

    render() {
        const {number, color, showing} = this.props
        return (
            <div className="block-outer">
                <div className="block-inner">
                    {
                        showing ? 
                            <div className="block-open">
                                <div className="block-number">{number}</div>
                                <div className="block-number-line" />
                            </div>
                            :
                            <div className="block-close">

                            </div>
                    }
                </div>
            </div>
        )
    }
}

export default Block