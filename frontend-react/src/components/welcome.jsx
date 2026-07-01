const Welcome = ({ onSubmit }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    const nom = e.target.nom.value.trim();
    const prenom = e.target.prenom.value.trim();
    const telephone = e.target.telephone.value.trim();
    if (!nom || !prenom || !telephone) return;
    onSubmit({ nom, prenom, telephone });
  };

  return (
    <div className="welcome-overlay">
      <div className="welcome-box">
        <div className="cca-logo" style={{ margin: "0 auto 16px" }}>
          <span className="logo-cca">CCA</span>
          <span className="logo-bank">BANK</span>
        </div>
        <h2>Bienvenue !</h2>
        <p>Avant de commencer, veuillez vous identifier.</p>
        <form onSubmit={handleSubmit}>
          <input name="nom" type="text" placeholder="Nom" required />
          <input name="prenom" type="text" placeholder="Prénom" required />
          <input name="telephone" type="tel" placeholder="Numéro de téléphone" required />
          <button type="submit">Commencer la conversation</button>
        </form>
      </div>
    </div>
  );
};

export default Welcome;