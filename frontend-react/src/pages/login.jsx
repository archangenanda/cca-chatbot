import { useState } from "react";

const Login = ({ onLogin }) => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [erreur, setErreur]     = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();

        const response = await fetch("http://localhost:8000/admin/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (data.token) {
            localStorage.setItem("token", data.token);
            onLogin();
        } else {
            setErreur("Identifiants incorrects !");
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <div className="login-logo">
                    <span className="logo-cca">CCA</span>
                    <span className="logo-bank">BANK</span>
                </div>
                <h2>Administration</h2>
                <p>Connectez-vous pour accéder au tableau de bord</p>

                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Nom d'utilisateur"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Mot de passe"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    {erreur && <p className="erreur">{erreur}</p>}
                    <button type="submit">Se connecter</button>
                </form>
            </div>
        </div>
    );
};

export default Login;