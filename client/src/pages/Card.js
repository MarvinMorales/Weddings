import React from "react";

export const Card = (props) => {
    return (
        <React.Fragment>
            <div className="card-container" >
                <div className="poster-container">
                    <div className="i-div"><i class="far fa-play-circle"></i></div>
                    <img className="poster" src={props.posterUrl}/>
                </div>
                <div className="footer-container">
                    <p className="title-wedding">{props.weddingName}</p>
                    <div>
                        <p>Video corto</p>
                        <i class="fas fa-arrow-right"></i>
                    </div>
                </div>
            </div>
        </React.Fragment>
    );
}