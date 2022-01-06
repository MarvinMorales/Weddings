import React from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { configuration } from "../config";

export const Login = () => {
    const [user, setUser] = React.useState(null);
    const [password, setPassword] = React.useState(null);
    const navigate = useNavigate();

    const validateCredentials = () => {
        if (user !== null && password !== null) {
            axios.post(`${configuration['host']}/auth`, {
                user: user, password: password
            }).then(response => {
                if (response.data['success']) {
                    window.localStorage.setItem('weddingsToken', response.data.token);
                    navigate('/uplader');
                } else alert("Las credenciales son incorrectas!");
            }).catch(err => console.error(err));
        } else alert("Se necesita llenar todos los campos!")
    }

    return (
        <React.Fragment>
            <section className="section1-login">
                <div className="form">
                    <h1>Login</h1>
                    <input onChange={event => setUser(event.target.value)} type="text" placeholder="Usuario..." required className="form-login-inputs"/>
                    <input onChange={event => setPassword(event.target.value)} type="password" placeholder="Password..." required className="form-login-inputs"/>
                    <input type="submit" onClick={ validateCredentials } className="form-login-inputs login-button" value="Entrar"/>
                </div>
            </section>
        </React.Fragment>
    );
}