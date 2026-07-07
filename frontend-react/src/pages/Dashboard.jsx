import { useState, useEffect } from "react";

// ── URL de l'API selon l'environnement ─────────────────────
// En local → localhost:8000, en production → Render
const API_URL = window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "https://cca-chatbot.onrender.com";

// ── Boutons filtre période ─────────────────────────────────
const FiltresPeriode = ({ valeur, onChange }) => (
    <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {["", "jour", "semaine", "mois"].map(p => (
            <button
                key={p}
                onClick={() => onChange(p)}
                style={{
                    padding: "4px 14px",
                    borderRadius: 20,
                    border: "1px solid #6a0dad",
                    background: valeur === p ? "#6a0dad" : "white",
                    color: valeur === p ? "white" : "#6a0dad",
                    cursor: "pointer",
                    fontSize: 13
                }}
            >
                {p === "" ? "Tout" : p.charAt(0).toUpperCase() + p.slice(1)}
            </button>
        ))}
    </div>
);

const Dashboard = ({ onLogout }) => {
    // ── États ──────────────────────────────────────────────
    const [faqs, setFaqs]         = useState([]);
    const [tickets, setTickets]   = useState([]);
    const [plaintes, setPlaintes] = useState([]);
    const [onglet, setOnglet]     = useState("faq");
    const [plainteSelectee, setPlainteSelectee] = useState(null);
    const [reponse, setReponse]   = useState("");
    const [nouveauStatut, setNouveauStatut] = useState("");
    const [filtreTicket, setFiltreTicket]   = useState("");
    const [filtrePlainte, setFiltrePlainte] = useState("");

    // ── Token d'authentification stocké dans localStorage ──
    const token = localStorage.getItem("token");

    // ── Charger les FAQ au montage du composant ────────────
    useEffect(() => {
        fetch(`${API_URL}/admin/faq`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(data => setFaqs(data));
    }, []);

    // ── Charger les tickets avec filtre de période ─────────
    const fetchTickets = (periode = "") => {
        const url = periode
            ? `${API_URL}/admin/tickets?periode=${periode}`
            : `${API_URL}/admin/tickets`;
        fetch(url, { headers: { Authorization: `Bearer ${token}` } })
            .then(res => res.json())
            .then(data => setTickets(data));
    };

    // ── Charger les plaintes avec filtre de période ────────
    const fetchPlaintes = (periode = "") => {
        const url = periode
            ? `${API_URL}/plaintes/?periode=${periode}`
            : `${API_URL}/plaintes/`;
        fetch(url, { headers: { Authorization: `Bearer ${token}` } })
            .then(res => res.json())
            .then(data => setPlaintes(data));
    };

    // ── Charger tickets et plaintes au montage ─────────────
    useEffect(() => { fetchTickets(); }, []);
    useEffect(() => { fetchPlaintes(); }, []);

    // ── Ouvrir le modal de gestion d'une plainte ───────────
    const ouvrirPlainte = (p) => {
        setPlainteSelectee(p);
        setReponse(p.reponse_admin || "");
        setNouveauStatut(p.statut);
    };

    // ── Sauvegarder le statut et la réponse admin ──────────
    const sauvegarderPlainte = () => {
        fetch(`${API_URL}/plaintes/${plainteSelectee.id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ statut: nouveauStatut, reponse_admin: reponse })
        })
        .then(() => {
            // Mettre à jour la liste localement sans recharger
            setPlaintes(prev => prev.map(p =>
                p.id === plainteSelectee.id
                    ? { ...p, statut: nouveauStatut, reponse_admin: reponse }
                    : p
            ));
            setPlainteSelectee(null);
        });
    };

    // ── Couleurs des badges de statut ──────────────────────
    const badgeStatut = {
        nouveau:  { background: "#e74c3c", color: "white" },
        en_cours: { background: "#f39c12", color: "white" },
        resolu:   { background: "#27ae60", color: "white" },
        ferme:    { background: "#95a5a6", color: "white" },
    };

    return (
        <div className="dashboard">

            {/* Header avec logo et bouton déconnexion */}
            <div className="dashboard-header">
                <div className="cca-logo">
                    <span className="logo-cca">CCA</span>
                    <span className="logo-bank">BANK</span>
                </div>
                <h1>Tableau de bord</h1>
                <button onClick={onLogout} className="logout-btn">
                    <span className="material-symbols-rounded">logout</span>
                    Déconnexion
                </button>
            </div>

            {/* Onglets de navigation */}
            <div className="dashboard-tabs">
                <button
                    className={onglet === "faq" ? "active" : ""}
                    onClick={() => setOnglet("faq")}
                >
                    <span className="material-symbols-rounded">quiz</span>
                    FAQ ({faqs.length})
                </button>
                <button
                    className={onglet === "tickets" ? "active" : ""}
                    onClick={() => setOnglet("tickets")}
                >
                    <span className="material-symbols-rounded">confirmation_number</span>
                    Tickets ({tickets.length})
                </button>
                <button
                    className={onglet === "plaintes" ? "active" : ""}
                    onClick={() => setOnglet("plaintes")}
                >
                    <span className="material-symbols-rounded">report</span>
                    Plaintes ({plaintes.length})
                </button>
            </div>

            {/* Contenu selon l'onglet actif */}
            <div className="dashboard-content">

                {/* Onglet FAQ */}
                {onglet === "faq" && (
                    <div className="faq-list">
                        <h2>Gestion des FAQ</h2>
                        {faqs.length === 0 ? (
                            <p>Aucune FAQ pour le moment.</p>
                        ) : (
                            faqs.map(faq => (
                                <div key={faq.id} className="faq-item">
                                    <span className="faq-categorie">{faq.categorie}</span>
                                    <p className="faq-question">{faq.question}</p>
                                    <p className="faq-reponse">{faq.reponse}</p>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {/* Onglet Tickets */}
                {onglet === "tickets" && (
                    <div className="tickets-list">
                        <h2>Tickets de réclamation</h2>
                        {/* Filtre par période */}
                        <FiltresPeriode
                            valeur={filtreTicket}
                            onChange={(p) => { setFiltreTicket(p); fetchTickets(p); }}
                        />
                        {tickets.length === 0 ? (
                            <p>Aucun ticket pour le moment.</p>
                        ) : (
                            tickets.map(ticket => (
                                <div key={ticket.id} className="ticket-item">
                                    <span className={`ticket-statut ${ticket.statut}`}>
                                        {ticket.statut}
                                    </span>
                                    <p>{ticket.message}</p>
                                    <small>{ticket.date}</small>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {/* Onglet Plaintes */}
                {onglet === "plaintes" && (
                    <div className="tickets-list">
                        <h2>Historique des plaintes</h2>
                        {/* Filtre par période */}
                        <FiltresPeriode
                            valeur={filtrePlainte}
                            onChange={(p) => { setFiltrePlainte(p); fetchPlaintes(p); }}
                        />
                        {plaintes.length === 0 ? (
                            <p>Aucune plainte pour le moment.</p>
                        ) : (
                            plaintes.map(p => (
                                <div key={p.id} className="ticket-item">
                                    {/* Badge de statut coloré */}
                                    <span style={{
                                        ...badgeStatut[p.statut],
                                        padding: "2px 10px",
                                        borderRadius: 12,
                                        fontSize: 12,
                                        fontWeight: "bold"
                                    }}>
                                        {p.statut}
                                    </span>
                                    <p>{p.message}</p>
                                    <small>
                                        {p.nom_client || "Anonyme"} —{" "}
                                        {new Date(p.date_soumission).toLocaleDateString("fr-FR")}
                                    </small>
                                    {/* Bouton pour ouvrir le modal de gestion */}
                                    <button
                                        onClick={() => ouvrirPlainte(p)}
                                        style={{ marginTop: 8, cursor: "pointer" }}
                                    >
                                        ✏️ Gérer
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                )}

            </div>

            {/* Modal de gestion d'une plainte */}
            {plainteSelectee && (
                <div style={{
                    position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
                    background: "rgba(0,0,0,0.5)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    zIndex: 1000
                }}>
                    <div style={{
                        background: "white", padding: 32, borderRadius: 12,
                        width: 480, boxShadow: "0 4px 20px rgba(0,0,0,0.2)"
                    }}>
                        <h3>Plainte #{plainteSelectee.id}</h3>
                        <p><strong>Client :</strong> {plainteSelectee.nom_client || "Anonyme"}</p>
                        <p><strong>Catégorie :</strong> {plainteSelectee.categorie || "Général"}</p>
                        <p><strong>Message :</strong> {plainteSelectee.message}</p>
                        <hr />
                        {/* Sélecteur de statut */}
                        <label><strong>Statut :</strong></label>
                        <select
                            value={nouveauStatut}
                            onChange={e => setNouveauStatut(e.target.value)}
                            style={{ display: "block", width: "100%", margin: "8px 0", padding: 8 }}
                        >
                            <option value="nouveau">nouveau</option>
                            <option value="en_cours">en_cours</option>
                            <option value="resolu">resolu</option>
                            <option value="ferme">ferme</option>
                        </select>
                        {/* Zone de réponse admin */}
                        <label><strong>Réponse admin :</strong></label>
                        <textarea
                            value={reponse}
                            onChange={e => setReponse(e.target.value)}
                            rows={4}
                            style={{ width: "100%", marginTop: 8, padding: 8 }}
                        />
                        <div style={{ display: "flex", gap: 12, marginTop: 16 }}>
                            <button
                                onClick={sauvegarderPlainte}
                                style={{
                                    background: "#6a0dad", color: "white",
                                    padding: "8px 20px", border: "none",
                                    borderRadius: 8, cursor: "pointer"
                                }}
                            >
                                💾 Sauvegarder
                            </button>
                            <button onClick={() => setPlainteSelectee(null)}>
                                Annuler
                            </button>
                        </div>
                    </div>
                </div>
            )}

        </div>
    );
};

export default Dashboard;