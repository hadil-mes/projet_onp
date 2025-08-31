function rafraichirLot(lotId) {
    fetch(`/api/lot/${lotId}`)
        .then(response => response.json())
        .then(data => {
            // Mettre à jour le prix actuel
            document.getElementById("prix-actuel").textContent = data.prix_actuel + " DH";

            // Mettre à jour le statut
            document.getElementById("statut").textContent = data.statut;

            // Mettre à jour l’historique
            let historique = document.getElementById("historique");
            historique.innerHTML = "";
            data.encheres.forEach(e => {
                let li = document.createElement("li");
                li.textContent = `💰 ${e.montant} DH (le ${e.date})`;
                historique.appendChild(li);
            });
        })
        .catch(err => console.error("Erreur API :", err));
}

// Rafraîchir toutes les 3 secondes
setInterval(() => {
    let lotId = document.body.dataset.lotId;
    if (lotId) {
        rafraichirLot(lotId);
    }
}, 3000);
