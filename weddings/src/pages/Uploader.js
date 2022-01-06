import React from "react";
import axios from 'axios';
import { configuration } from "../config";

export const Uploader = () => {
    const [image, setImage] = React.useState(null);
    const [loading, setLoading] = React.useState(false);
    const [percent, setPercent] = React.useState(0);
    const [imageName, setImageName] = React.useState("Drop your video here!");
    const [videoURL, setVideoURL] = React.useState(null);

    const handleImage = event => {
        setImage(event.target.files[0]);
        setImageName(event.target.files[0].name);
    }

    const handleUploadImage = () => {
        let formData = new FormData();
        formData.append('image', image, image.name);
        axios.post(`${configuration['host']}/upload/file/video`, formData, {
            headers: {
                "Authorization": window.localStorage.getItem('weddingsToken'), 
                "Content-Type": "multipart/form-data",
                "Access-Control-Allow-Origin": "*"
            }, onUploadProgress: progress => setPercent(Math.round(progress.loaded / progress.total * 100))
        }).then(response => { if (response.data['success']) setLoading(!loading) })
        .catch(err => console.error(err));
    }

    return (
        <div className="App">
        <section className='section1'>
            <section className='section2'>
            <article className='art1'>
            <div className='image-drop-container'>
                <div className='cell'>
                <input className='cell-1' onChange={ handleImage } type="file" name="filename"/>
                <div className='icon'>
                    <i className="fas fa-cloud-upload-alt"></i>
                    <h1 className='title'>{ imageName.length > 24 ? imageName.substring(0, 20) + "..." : imageName }</h1>
                </div>
                </div>
            </div>
            </article>
            <article className='art2'>
                <button onClick={ handleUploadImage } className='button-upload'>Upload File</button>
                <div className='line1'>
                <p><strong>{percent}%</strong> <span style={{fontSize: 12, fontStyle: 'italic',}}>Uploaded</span></p>
                <div className='loaderContainer'>
                    <div className='loaderBar' style={{width: `${percent}%`}}></div>
                </div>
                </div>
            </article>
            <article className={ percent === 100 ? 'art3-anim' : 'art3' }>
                { loading ? <div className='completed'><i class="fas fa-thumbs-up"></i><p>Completed!</p></div> : 
                <img  className='loading' src='https://i.pinimg.com/originals/a2/dc/96/a2dc9668f2cf170fe3efeb263128b0e7.gif'/> }
            </article>
            </section>
        </section>
        </div>
    );
}