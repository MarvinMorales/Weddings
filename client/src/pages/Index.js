import React from 'react';
import Carroussel from './Carrousel';
import { v4 as uuidv4 } from "uuid";
import { Card } from './Card';

export const Index = () => {
    const slides = [
        {
            key: uuidv4(),
            content: <Card weddingName="Boda de Brandon + Andrea" posterUrl="https://www.phillymag.com/wp-content/uploads/sites/3/2021/10/main-3.jpg"/>
        },
        {
            key: uuidv4(),
            content: <Card weddingName="Boda de Brandon + Andrea" posterUrl="https://www.theknot.com/tk-media/images/e5fb7303-e0bf-49e6-826b-1322244936a8"/>
        },
        {
            key: uuidv4(),
            content: <Card weddingName="Boda de Brandon + Andrea" posterUrl="https://weddingstylemagazine.com/sites/default/files/styles/flexslider_full/public/sergio-sandona-ss21-real-wedding-belinda-hadrien-08.jpg"/>
        },
        {
            key: uuidv4(),
            content: <Card weddingName="Boda de Brandon + Andrea" posterUrl="https://www.phillymag.com/wp-content/uploads/sites/3/2021/10/main-3.jpg"/>
        },
        {
            key: uuidv4(),
            content: <Card weddingName="Boda de Brandon + Andrea" posterUrl="https://www.theknot.com/tk-media/images/e5fb7303-e0bf-49e6-826b-1322244936a8"/>
        },
        {
            key: uuidv4(),
            content: <Card weddingName="Boda de Brandon + Andrea" posterUrl="https://weddingstylemagazine.com/sites/default/files/styles/flexslider_full/public/sergio-sandona-ss21-real-wedding-belinda-hadrien-08.jpg"/>
        }
    ]

    return (
        <React.Fragment>
            <section className='data-over-video'>
                <header className='header-number1'>
                    <div className='logo-container'>
                        <div className='logo-circle'><img src="https://img.myloview.com/stickers/fc-logo-letter-design-on-luxury-background-cf-logo-monogram-initials-letter-concept-ec-icon-logo-design-ce-elegant-and-professional-letter-icon-design-on-black-background-ec-ce-cf-fc-400-234447751.jpg"/></div>
                        <div className='logo-description'>
                            <h2 className='logoTitle'>Gabriel Loor Prod.</h2>
                            <p className='logoDesc' id='learn-more' onClick={() => alert(1)}>Learn more</p>
                        </div>
                    </div>
                    <div className='icons-container'>
                        <div> <i className="fas fa-cloud-download-alt"></i></div>
                        <div> <i className="fas fa-share-alt"></i></div>
                    </div>
                </header>
                <article className="row-name">
                    <h1>Boda de ALex + Andrea</h1>
                    <div><p className='trailer'>Trailer</p></div>
                    <div className='play-all'>
                        <i className="far fa-play-circle"></i>
                        <p>Play all</p>
                    </div>
                </article>
                <article className="video-cards">
                <Carroussel
                    cards={slides}
                    height="500px"
                    width="80%"
                    margin="0 auto"
                    offset={3}
                    showArrows={false}
                />
                </article>
            </section>
            <section className='sectionVideo'>
                <video className='video-back' loop autoPlay={true} muted src={require("../media/vid.mp4")}></video>
            </section>
        </React.Fragment>
    );
}