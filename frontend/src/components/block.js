import React from 'react';
import './block.css';

function Block(props) {
    const {index, number, color, showing} = props
    
    return (
        <div 
            onClick={() => props.onClick(index)} 
            className={`block-outer block-color-${color}`}
        >
            <div className="block-inner">
                {
                    showing ? 
                        <div className="block-open">
                            <div className="block-number">{number}</div>
                            <div className="block-number-line" />
                        </div>
                        :
                        <div className="block-close">
                            <div className="block-close-dot-container">
                                <div className="block-close-dot-wrapper-right">
                                    <div className="block-close-dot" />
                                </div>
                                <div className="block-close-dot-wrapper-center">
                                    <div className="block-close-dot" />
                                </div>
                                <div className="block-close-dot-wrapper-left">
                                    <div className="block-close-dot" />
                                </div>
                                <div className="block-close-dot-wrapper-center">
                                    <div className="block-close-dot" />
                                </div>
                                <div className="block-close-dot-wrapper-right">
                                    <div className="block-close-dot" />
                                </div>
                            </div>
                        </div>
                }
            </div>
        </div>
    )
}

export default Block