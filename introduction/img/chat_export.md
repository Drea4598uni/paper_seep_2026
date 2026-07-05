# Costo computazionale di simulazioni CFD di turbine e wind farm — log della chat

> Esportazione della conversazione (ricostruita dal contesto della sessione).
> Data: giugno 2026. Lingua: italiano (messaggi utente verbatim; risposte sintetizzate fedelmente).

## Indice
1. Richiesta iniziale e chiarimenti
2. Costruzione del modello dei costi (24 casi)
3. Report Word + Excel
4. Iterazioni successive (celle, dominio, flow-through, layout)
5. Infografiche e grafico di selezione
6. Scenario "riproduzione delle scie" (ricalcolo)
7. Versione IEEE / SciencePlots
8. Assunzioni finali del modello
9. Risultati finali (tabella 24 casi)
10. Deliverable e come rigenerarli

---

## 1. Richiesta iniziale e chiarimenti

**Utente:**
> ho bisogno che fai una ricerca bibliografica su articoli scientifici e mi stimi qual è la richiesta di ore di calcolo e le dimensioni della griglia per le seguenti simulazioni:
> 1. singola wind turbine, full geometry (no actuator line/disk)
> 2. singola wind turbine, modellazione actuator line / disk
> 3. wind farm con 20 turbine, full geometry
> 4. wind farm con 40 turbine, full geometry
> 5. wind farm con 20 turbine, actuator line / disk
> 6. wind farm con 40 turbine, actuator line / disk
>
> Combinare le 6 casistiche con: 1) LES con boundary layer atmosferico, 2) URANS con ABL; e due taglie: 5 MW e 15 MW. Griglia 6×2×2 = 24 opzioni con carico computazionale, numero di celle, durata su HPC tipo CINECA, spesa elettrica (incluso riscaldamento). Una sola simulazione, una sola velocità del vento. Report in inglese con references agli ultimi 10 anni e assunzioni esplicitate. Chiedere chiarimenti prima di iniziare.

**Assistente:** ho posto 4 domande di chiarimento (via tool a scelta multipla). Risposte ricevute:
- **Sistema HPC:** Leonardo CINECA (CPU + GPU).
- **Formato:** Report Word + tabella Excel.
- **Prezzo energia / PUE:** EU media ~0,15 €/kWh, PUE 1,2.
- **Durata simulata:** "standard di settore".

Nessun connettore esterno necessario: ricerca via web search integrata.

---

## 2. Costruzione del modello dei costi (24 casi)

**Ricerca bibliografica** (ancoraggi principali):
- URANS blade-resolved NREL 5 MW: ~55 M celle, ~16.300 CPU-h per statistiche convergenti (Journal of Physics CS 1618:052007).
- LES blade-resolved in ABL: ExaWind fino a ~6 miliardi di punti per la NREL 5 MW.
- Wind farm LES actuator (SOWFA): fino a ~1 miliardo di celle; raffinamento ~0,3 m vicino al rotore; ALM con passo ~5× più fine e dt 20–40× più piccolo dell'ADM.
- Leonardo CINECA: Booster 3.456 nodi (4×A100 64 GB + Ice Lake 32-core); DCGP 1.536 nodi (2×Xeon 8480+ 56-core); ~7,5 MW totali.

**Modello** (mesh bottom-up, time-stepping, core-hours = celle × step × C / 3600, mappatura su Leonardo, energia = node-h × potenza × PUE, costo = energia × 0,15 €/kWh). Verifica numerica indipendente di tutti i 24 casi + riproduzione dell'ancoraggio di letteratura (~16.500 vs ~16.300 CPU-h).

---

## 3. Report Word + Excel

**Assistente:** prodotti `Wind_CFD_Computational_Cost_Report.docx` (report in inglese, metodologia, assunzioni, tabella 24 casi in landscape, 15 reference 2014–2024) e `wind_cfd_cost_grid.xlsx` (foglio Assumptions + 24 cases, filtrabile).

---

## 4. Iterazioni successive

**Utente:** «spiegami come hai stimato wind farm 20 turbine LES + actuator line» → spiegazione passo-passo (celle, step, core-hours, mappatura GPU, energia, costo).

**Utente:** «dimensioni rotore 5m e 15 mw?» → NREL 5 MW: D = 126 m; IEA 15 MW: D = 240 m (con hub, rpm, velocità nominali).

**Utente:** «le celle nella zona raffinata che dimensione hanno?» → blade-resolved: prima cella a parete y⁺≈1 ~10⁻⁵ m; actuator: box rotore/scia ~0,3–2 m (~D/100).

**Utente:** «inserisci una stima delle dimensioni minime delle celle nella zona di massimo refinement, e aggiungi una colonna con le dimensioni in diametri e una col diametro» → aggiunte colonne Rotor D (m), Min cell Δx (m), Δx/D + sottosezione metodologica 3.6.

**Utente:** «aggiungi una colonna con le dimensioni del dominio di calcolo» → aggiunta colonna dominio (in D e in km): single 24×8×6 D, farm20 44×26×6 D, farm40 64×32×6 D.

**Utente:** «metti le dimensioni del dominio in diametri… aggiungi flow-through times stimati per la convergenza e il numero di rivoluzioni del rotore» → ricostruito il modello temporale fisico (U=10 m/s, rpm 12/7,5, dt da CFL/azimut), aggiunte colonne Flow-throughs e Rotor revs.

**Utente:** «come hai posizionato le turbine nella farm?» → il modello non usa coordinate esplicite; layout implicito coerente con array allineato 5×4 (farm20) e 8×5 (farm40), spaziatura ~7×5 D.

**Utente:** «aggiungi queste info come nota metodologica nel documento e aggiorna l'Excel» → aggiunta §3.7 (layout) + colonne Layout e Spacing nell'Excel.

---

## 5. Infografiche e grafico di selezione

**Utente:** richiesta di un'infografica con assi x in basso (1: grid size & min Δx; 2: core-hours & wall-days; 3: energy; 4: energy cost) e i casi sopra → prodotto widget interattivo a **coordinate parallele**.

**Utente:** «come si chiama il grafico?» → *parallel coordinates plot*.

**Utente:** «esporta in maniera editabile e trova una visualizzazione non dinamica per un paper» → esportate versioni vettoriali (SVG/PDF + script): parallel coordinates, dot-plot small multiples, heatmap.

**Utente:** «mi aspettavo qualcosa tipo il diagramma di selezione delle turbine idrauliche; le immagini confondono» → creato il **nomogramma di selezione** (`fig_selection_chart`): x = celle, y = time-step (log-log), diagonali = iso–core-hours, bande = regimi di costo/fattibilità, punti = 24 casi.

**Iterazioni grafico:** font Arial; etichette `S 5 MW` / `WF 20x5 MW`; legenda in alto a sinistra; costi € sulle iso-linee; simboli diversi single (triangolo) / farm (cerchio); rimozione leader; etichette iso-costo riposizionate e inclinate secondo la pendenza reale delle linee; inversione colori (full geometry = verde, actuator = rosso).

---

## 6. Scenario "riproduzione delle scie" (ricalcolo)

**Utente:** «perché le URANS full geometry fanno meno iterazioni delle actuator line?» → perché (nell'ipotesi iniziale) il blade-resolved convergeva i soli carichi (30/15 giri, <1 flow-through), mentre l'actuator convergeva le statistiche di scia (6–14 flow-through); dt simile, cambia il tempo fisico simulato.

**Utente:** «rifai i conti tenendo conto che le simulazioni debbano riprodurre le scie e non solo i carichi» → **modificato il modello**: tutti i casi (anche blade-resolved) girano per diversi flow-through. Effetto: i blade-resolved esplodono.
- Range nuovo: da ~40.000 core-h / €65 (actuator URANS/LES singola) a **~45,8 miliardi core-h / €34,3 M / ~228.900 MWh / ~34 anni** (blade-resolved LES farm 40×15 MW) → oltre l'exascale, irrealizzabile.
- Conclusione: studi di scia su wind farm fattibili **solo con modelli actuator**.

**Utente:** «aggiorna il Word e l'Excel, salva script e dati» → report e Excel riallineati allo scenario "scie"; salvati tutti gli script e `cases.json`.

---

## 7. Versione IEEE / SciencePlots

**Utente:** richiesta di un grafico aggiuntivo con stile `scienceplots(['science','ieee'])` e rcParams specifici, senza cancellare il precedente → creato `make_selection_chart_ieee.py` → `fig_selection_chart_ieee.{svg,pdf,png}`. Usato `['science','ieee','no-latex']` perché le etichette contengono €, ×, Δ in Unicode incompatibili con il rendering LaTeX di `science`.

**Utente:** chiarimenti sulle etichette delle iso-linee e sulla didascalia in basso a destra:
- `10ⁿ core-h` = numero di core-hours della linea; `€X–€Y` = costo elettrico, basso = GPU (Booster), alto = CPU (DCGP).
- `C ≈ 2.5×10⁻⁵ core-s/cell/step` = costo del solutore per cella/step usato per posizionare le iso-linee (core-hours = celle × step × C / 3600).
- `cost = Booster(GPU)–DCGP(CPU)` = i due estremi del range corrispondono alle due partizioni di Leonardo.

---

## 8. Assunzioni finali del modello

**Hardware (Leonardo CINECA)**
- DCGP (CPU, per URANS): 112 core/nodo, ~1,1 kW/nodo.
- Booster (GPU, per LES): ~2,5 kW/nodo; 1 nodo Booster ≈ 600 core CPU equivalenti (FV-CFD).

**Energia/costo:** PUE 1,2; 0,15 €/kWh.

**Costo solutore C (core-s/cella/step):** URANS 2×10⁻⁴; LES 3×10⁻⁵ (media per iso-linee 2,5×10⁻⁵).

**Celle per turbina (baseline 5 MW):** full-geom URANS 60 M, LES 350 M; actuator URANS 6 M, LES 15 M. Sfondo ABL: single 4/40 M, farm20 20/200 M, farm40 35/350 M (URANS/LES). Fattore taglia 15 MW: ×1,8 (full-geom), ×1,4 (actuator).

**Cella minima (zona di max raffinamento):** full-geom y⁺≈1 → 1×10⁻⁵ m (LES) / 2×10⁻⁵ m (URANS); actuator → D/100 (LES) / D/64 (URANS).

**Dominio (in D):** single 24×8×6; farm20 44×26×6; farm40 64×32×6. Layout: farm20 5×4, farm40 8×5; spaziatura ~7×5 D.

**Tempo / convergenza (scenario "scie", tutti i casi):** U = 10 m/s; rpm 12 (5 MW) / 7,5 (15 MW). Flow-through per convergenza: URANS 6/8/10, LES 10/12/14 (single/20/40). dt: full-geom URANS = 2° azimut; full-geom LES = 1×10⁻⁴ s; actuator = Δx_min/V_tip.

---
## 9. Risultati finali (scenario "scie", 24 casi)

| # | Scale | Geom | Model | MW | Domain (D) | Flow-thr. | Rotor revs | Mesh (M cells) | Min dx (m) | Core-hours | Wall (days) | Energy (MWh) | Cost (EUR) |
|---|-------|------|-------|----|-----------|-----------|-----------|----------------|-----------|------------|-------------|--------------|------------|
| 1 | Single | Full geom | LES | 5 | 24×8×6 | 10 | 605 | 390 | 1e-05 | 98,280,000 | 106.6 | 491 | 73,710 |
| 1 | Single | Full geom | LES | 15 | 24×8×6 | 10 | 720 | 670 | 1e-05 | 321,600,000 | 349.0 | 1,608 | 241,200 |
| 1 | Single | Full geom | URANS | 5 | 24×8×6 | 6 | 363 | 64 | 2e-05 | 232,245 | 5.4 | 3 | 411 |
| 1 | Single | Full geom | URANS | 15 | 24×8×6 | 6 | 432 | 112 | 2e-05 | 483,840 | 11.2 | 6 | 855 |
| 2 | Single | Actuator | LES | 5 | 24×8×6 | 10 | 605 | 55 | 1.26 | 87,085 | 0.2 | 0 | 65 |
| 2 | Single | Actuator | LES | 15 | 24×8×6 | 10 | 720 | 61 | 2.40 | 114,982 | 0.2 | 1 | 86 |
| 2 | Single | Actuator | URANS | 5 | 24×8×6 | 6 | 363 | 10 | 1.97 | 40,534 | 0.9 | 0 | 72 |
| 2 | Single | Actuator | URANS | 15 | 24×8×6 | 6 | 432 | 12 | 3.75 | 59,836 | 1.4 | 1 | 106 |
| 3 | 20 | Full geom | LES | 5 | 44×26×6 | 12 | 1,331 | 7,200 | 1e-05 | 3,991,680,000 | 1082.8 | 19,958 | 2,993,760 |
| 3 | 20 | Full geom | LES | 15 | 44×26×6 | 12 | 1,584 | 12,800 | 1e-05 | 13,516,800,000 | 3666.7 | 67,584 | 10,137,600 |
| 3 | 20 | Full geom | URANS | 5 | 44×26×6 | 8 | 887 | 1,220 | 2e-05 | 10,821,942 | 62.9 | 128 | 19,132 |
| 3 | 20 | Full geom | URANS | 15 | 44×26×6 | 8 | 1,056 | 2,180 | 2e-05 | 23,020,800 | 133.8 | 271 | 40,697 |
| 4 | 40 | Full geom | LES | 5 | 64×32×6 | 14 | 2,258 | 14,350 | 1e-05 | 13,500,480,000 | 3662.2 | 67,502 | 10,125,360 |
| 4 | 40 | Full geom | LES | 15 | 64×32×6 | 14 | 2,688 | 25,550 | 1e-05 | 45,785,600,000 | 12420.1 | 228,928 | 34,339,200 |
| 4 | 40 | Full geom | URANS | 5 | 64×32×6 | 10 | 1,613 | 2,435 | 2e-05 | 39,271,680 | 228.3 | 463 | 69,427 |
| 4 | 40 | Full geom | URANS | 15 | 64×32×6 | 10 | 1,920 | 4,355 | 2e-05 | 83,616,000 | 486.0 | 985 | 147,821 |
| 5 | 20 | Actuator | LES | 5 | 44×26×6 | 12 | 1,331 | 500 | 1.26 | 1,741,700 | 3.8 | 9 | 1,306 |
| 5 | 20 | Actuator | LES | 15 | 44×26×6 | 12 | 1,584 | 620 | 2.40 | 2,571,083 | 5.6 | 13 | 1,928 |
| 5 | 20 | Actuator | URANS | 5 | 44×26×6 | 8 | 887 | 140 | 1.97 | 1,387,167 | 8.1 | 16 | 2,452 |
| 5 | 20 | Actuator | URANS | 15 | 44×26×6 | 8 | 1,056 | 188 | 3.75 | 2,217,585 | 12.9 | 26 | 3,920 |
| 6 | 40 | Actuator | LES | 5 | 64×32×6 | 14 | 2,258 | 950 | 1.26 | 5,615,664 | 12.2 | 28 | 4,212 |
| 6 | 40 | Actuator | LES | 15 | 64×32×6 | 14 | 2,688 | 1,190 | 2.40 | 8,374,238 | 18.2 | 42 | 6,281 |
| 6 | 40 | Actuator | URANS | 5 | 64×32×6 | 10 | 1,613 | 275 | 1.97 | 4,954,171 | 28.8 | 58 | 8,758 |
| 6 | 40 | Actuator | URANS | 15 | 64×32×6 | 10 | 1,920 | 371 | 3.75 | 7,956,693 | 46.3 | 94 | 14,066 |

**Range:** core-hours 40,534 - 45,785,600,000 ; costo EUR 65 - 34,339,200.

---

## 10. Deliverable e come rigenerarli

**Documenti**
- Wind_CFD_Computational_Cost_Report.docx  — report in inglese (scenario scie).
- wind_cfd_cost_grid.xlsx  — griglia 24 casi + foglio assunzioni.

**Figure (vettoriali SVG/PDF + anteprima PNG)**
- fig_selection_chart.{svg,pdf,png}  — nomogramma di selezione (stile Arial).
- fig_selection_chart_ieee.{svg,pdf,png}  — stessa figura, stile SciencePlots/IEEE.
- fig_parallel_coordinates.*, fig_dotplot_small_multiples.*, fig_heatmap.*

**Script e dati**
- model.py  — modello dei costi: genera cases.json e l'Excel.
- cases.json  — dati dei 24 casi (input di figure e report).
- make_selection_chart.py, make_selection_chart_ieee.py, make_figures.py  — figure.
- build_report.js  — generatore del report Word (richiede: npm install docx).

**Rigenerazione:** eseguire `python3 model.py`, poi `python3 make_selection_chart.py` / `make_selection_chart_ieee.py` / `make_figures.py` per le figure e `node build_report.js` per il Word.

