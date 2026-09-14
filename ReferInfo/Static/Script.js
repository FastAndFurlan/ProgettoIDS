document.addEventListener("DOMContentLoaded", function () {
    caricaProvince();
    caricaGraficoAffluenza();
    caricaGraficoGeografico();
    caricaGraficoQuesiti();
});

function caricaProvince() {
    const data = document.getElementById("app-data");
    if (!data) return; // se data non esiste

    const provinceRegione = JSON.parse(data.getAttribute("data-province"));
    const selezioneRegione = document.getElementById("regione");
    const selezioneProvincia = document.getElementById("provincia");
    if (!selezioneRegione || !selezioneProvincia) return; // le due select non esistono

    selezioneRegione.addEventListener("change", function () {
        const regioneSelezionata = this.value;
        selezioneProvincia.innerHTML = "<option value=''>Seleziona una provincia</option>";

        if (regioneSelezionata && provinceRegione[regioneSelezionata]) {
            selezioneProvincia.disabled = false; // abilito selezione provincia
            provinceRegione[regioneSelezionata].forEach(provincia => {
                const option = document.createElement("option");
                option.value = provincia;
                option.textContent = provincia;
                selezioneProvincia.appendChild(option);
            });
        } else {
            selezioneProvincia.disabled = true;
            selezioneProvincia.innerHTML = '<option value="">Prima seleziona una Regione</option>';
        }
    });
}

function caricaGraficoAffluenza() {
    const datiEl = document.getElementById("dati-andamento");
    const ctx = document.getElementById("graficoAffluenza");
    if (!datiEl || !ctx) return; // niente dati o niente canvas -> non disegnare nulla

    const datiAndamento = JSON.parse(datiEl.textContent);

    new Chart(ctx, {
        type: "line",
        data: {
            labels: datiAndamento.map(d => d.ANNO),
            datasets: [{
                label: "Affluenza %",
                data: datiAndamento.map(d => d.affluenza_pct),
                borderColor: "navy",
                backgroundColor: "rgba(0,0,128,0.1)",
                fill: true,
                tension: 0.2,
            }]
        },
        options: {
            scales: {
                y: { min: 0, max: 100, title: { display: true, text: "Affluenza %" } }
            }
        }
    });
}

function caricaGraficoGeografico() {
    const datiEl = document.getElementById("dati-geografico");
    const ctx = document.getElementById("graficoGeografico");
    if (!datiEl || !ctx) return;

    const datiGeografico = JSON.parse(datiEl.textContent);
    if (datiGeografico.length === 0) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: datiGeografico.map(d => d.nome),
            datasets: [{
                label: "Affluenza %",
                data: datiGeografico.map(d => d.affluenza_pct),
                backgroundColor: "navy",
            }]
        },
        options: {
            indexAxis: "y",
            scales: { x: { min: 0, max: 100 } }
        }
    });
}

function caricaGraficoQuesiti() {
    const datiEl = document.getElementById("dati-quesiti");
    const ctx = document.getElementById("graficoQuesiti");
    if (!datiEl || !ctx) return;

    const datiQuesiti = JSON.parse(datiEl.textContent);
    if (datiQuesiti.length === 0) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: datiQuesiti.map(d => d.QUESITO.substring(0, 40) + "..."),
            datasets: [{
                label: "Affluenza %",
                data: datiQuesiti.map(d => d.affluenza_pct),
                backgroundColor: "gold",
            }]
        },
        options: {
            scales: { y: { min: 0, max: 100 } }
        }
    });
}