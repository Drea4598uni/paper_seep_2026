const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, LevelFormat, HeadingLevel, BorderStyle, WidthType,
  ShadingType, PageOrientation, ExternalHyperlink, Footer, Header,
  PageNumber, TabStopType, TabStopPosition
} = require("docx");

const cases = JSON.parse(fs.readFileSync("cases.json", "utf8"));

const NAVY = "1F4E78", LIGHT = "EAF1F8", WARM = "FBEEE6", GREY = "808080";
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

function H1(t){return new Paragraph({heading:HeadingLevel.HEADING_1,children:[new TextRun(t)]});}
function H2(t){return new Paragraph({heading:HeadingLevel.HEADING_2,children:[new TextRun(t)]});}
function P(t,opts={}){return new Paragraph({spacing:{after:140,line:276},children:[new TextRun({text:t,...opts})]});}
function bullet(runs){return new Paragraph({numbering:{reference:"b",level:0},spacing:{after:60},children:runs});}
function R(t,o={}){return new TextRun({text:t,...o});}

// number helpers
const fInt = n => Math.round(n).toLocaleString("en-US");
const f1 = n => n.toLocaleString("en-US",{minimumFractionDigits:1,maximumFractionDigits:1});
const f2 = n => n.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2});
function coreH(n){ if(n>=1e6) return (n/1e6).toFixed(2)+"M"; if(n>=1e3) return (n/1e3).toFixed(0)+"k"; return Math.round(n).toString(); }
function sup(e){const m={'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'};return String(e).split('').map(c=>m[c]).join('');}
function sci(x){const e=Math.floor(Math.log10(x));const m=x/Math.pow(10,e);return m.toFixed(1)+"×10"+sup(e);}
function fmtM(x){return x>=0.01?x.toFixed(2):sci(x);}        // metres
function fmtDoverD(x){return x>=1e-3?x.toFixed(4):sci(x);}   // fraction of D

// ---------- TABLE (landscape) ----------
const headers = ["#","Configuration","Model","MW","Rotor D\n(m)","Domain\n(in D)","Flow-\nthroughs","Rotor\nrevs","Mesh\n(M cells)","Min cell\nΔx (m)","Δx / D","Core-\nhours","Wall\n(days)","Energy\n(MWh)","Cost\n(EUR)"];
const colW = [340, 2700, 640, 480, 600, 950, 880, 860, 1000, 1230, 980, 1280, 950, 1000, 1230]; // sums 15120
const tableW = colW.reduce((a,b)=>a+b,0);
const fttFmt = x => x>=1 ? x.toFixed(0) : x.toFixed(2);

function hCell(t,i){
  return new TableCell({borders,width:{size:colW[i],type:WidthType.DXA},
    shading:{fill:NAVY,type:ShadingType.CLEAR},margins:{top:50,bottom:50,left:50,right:50},
    children: t.split("\n").map(line=>new Paragraph({alignment:AlignmentType.CENTER,
      children:[new TextRun({text:line,bold:true,color:"FFFFFF",size:13})]}))});
}
function dCell(t,i,fill,align){
  return new TableCell({borders,width:{size:colW[i],type:WidthType.DXA},
    shading:{fill,type:ShadingType.CLEAR},margins:{top:36,bottom:36,left:50,right:50},
    children:[new Paragraph({alignment:align||AlignmentType.CENTER,
      children:[new TextRun({text:t,size:13})]})]});
}

const headerRow = new TableRow({tableHeader:true,children:headers.map((h,i)=>hCell(h,i))});
const dataRows = cases.map(r=>{
  const fill = r.model==="LES"?LIGHT:WARM;
  const cells = [
    dCell(r.case,0,fill),
    dCell(r.config,1,fill,AlignmentType.LEFT),
    dCell(r.model,2,fill),
    dCell(String(r.size_MW),3,fill),
    dCell(String(r.rotor_D_m),4,fill),
    dCell(r.domain_D,5,fill),
    dCell(fttFmt(r.flow_throughs),6,fill),
    dCell(fInt(r.rotor_revs),7,fill),
    dCell(f1(r.cells_M),8,fill),
    dCell(fmtM(r.dx_min_m),9,fill),
    dCell(fmtDoverD(r.dx_over_D),10,fill),
    dCell(coreH(r.core_hours),11,fill),
    dCell(f2(r.wall_days),12,fill),
    dCell(f2(r.energy_MWh),13,fill),
    dCell(fInt(r.cost_EUR),14,fill),
  ];
  return new TableRow({children:cells});
});
const grid = new Table({width:{size:tableW,type:WidthType.DXA},columnWidths:colW,
  rows:[headerRow,...dataRows]});

// ---------- references ----------
function ref(num, text, url){
  return new Paragraph({spacing:{after:100},indent:{left:360,hanging:360},
    children:[ new TextRun({text:`[${num}] `,bold:true}), new TextRun(text+" "),
      new ExternalHyperlink({children:[new TextRun({text:url,style:"Hyperlink",size:18})],link:url}) ]});
}

const refs = [
["Sebastiani, A., et al. (2024). Blade-resolved numerical simulations of the NREL offshore 5 MW baseline wind turbine in full scale: a study of proper solver configuration and discretization strategies. Energy, 254.","https://www.sciencedirect.com/science/article/abs/pii/S0360544222012713"],
["Study on the influence of the numerical scheme on the accuracy of blade-resolved simulations of the NREL 5 MW rotor in full scale (2023). Energy, 283.","https://www.sciencedirect.com/science/article/abs/pii/S0360544223017887"],
["Sharma, A., et al. (2024). ExaWind: Open-source CFD for hybrid-RANS/LES geometry-resolved wind turbine simulations in atmospheric flows. Wind Energy, 27(3).","https://onlinelibrary.wiley.com/doi/10.1002/we.2886"],
["ExaWind Project demonstrates blade-resolved simulation of the NREL 5 MW reference wind turbine. Exascale Computing Project (2021).","https://www.exascaleproject.org/exawind-project-demonstrates-blade-resolved-simulation-of-the-nrel-5-mw-reference-wind-turbine/"],
["Kirby, A. C., et al. (2019). Wind farm simulations using an overset hp-adaptive approach with blade-resolved turbine models. Int. J. High Performance Computing Applications, 33(5).","https://journals.sagepub.com/doi/10.1177/1094342019832960"],
["Blade-Resolved CFD Simulations of a Periodic Array of NREL 5 MW Rotors with and without Towers (2022). Wind, 2(1), 4.","https://www.mdpi.com/2674-032X/2/1/4"],
["Deskos, G., et al. (2018). Mesh-adaptive simulations of horizontal-axis turbine arrays using the actuator line method. Wind Energy, 21(12).","https://onlinelibrary.wiley.com/doi/full/10.1002/we.2253"],
["Ribeiro, A. F. P., et al. (2024). Sliding mesh simulations of a wind turbine rotor with actuator line lattice-Boltzmann method. Wind Energy, 27(6).","https://onlinelibrary.wiley.com/doi/full/10.1002/we.2821"],
["Joulin, P.-A., et al. (2019). The Actuator Line Method in the meteorological LES model Meso-NH to analyze the Horns Rev 1 wind farm photo case. Frontiers in Earth Science, 7, 350.","https://www.frontiersin.org/journals/earth-science/articles/10.3389/feart.2019.00350/full"],
["Sebastiani, A., et al. (2021). Data analysis and simulation of the Lillgrund wind farm. Wind Energy, 24(6).","https://onlinelibrary.wiley.com/doi/full/10.1002/we.2594"],
["Mehta, D., et al. (2014). Large eddy simulation of wind farm aerodynamics: a review. Renewable & Sustainable Energy (survey of high-fidelity wind-farm LES methods).","https://pmc.ncbi.nlm.nih.gov/articles/PMC5346217/"],
["Stevens, R. J. A. M., Graham, J., Meneveau, C. (2014). A concurrent precursor inflow method for LES and applications to finite-length wind farms.","https://www.academia.edu/24935738/A_concurrent_precursor_inflow_method_for_Large_Eddy_Simulations_and_applications_to_finite_length_wind_farms"],
["Wind Turbine Large-Eddy Simulations on Very Coarse Grid Resolutions using an Actuator Line Model (2016). arXiv:1605.03153.","https://arxiv.org/pdf/1605.03153"],
["Turisini, M., Amati, G., Cestari, M. (2023). LEONARDO: A Pan-European Pre-Exascale Supercomputer for HPC and AI Applications. arXiv:2307.16885.","https://arxiv.org/pdf/2307.16885"],
["CINECA. Leonardo HPC system - technical specifications (Booster & DCGP partitions).","https://leonardo-supercomputer.cineca.eu/hpc-system/"],
];

// ---------- document ----------
const doc = new Document({
  styles:{
    default:{document:{run:{font:"Arial",size:21}}},
    paragraphStyles:[
      {id:"Heading1",name:"Heading 1",basedOn:"Normal",next:"Normal",quickFormat:true,
        run:{size:30,bold:true,font:"Arial",color:NAVY},
        paragraph:{spacing:{before:280,after:160},outlineLevel:0}},
      {id:"Heading2",name:"Heading 2",basedOn:"Normal",next:"Normal",quickFormat:true,
        run:{size:24,bold:true,font:"Arial",color:NAVY},
        paragraph:{spacing:{before:200,after:120},outlineLevel:1}},
    ]
  },
  numbering:{config:[
    {reference:"b",levels:[{level:0,format:LevelFormat.BULLET,text:"•",alignment:AlignmentType.LEFT,
      style:{paragraph:{indent:{left:560,hanging:280}}}}]},
  ]},
  sections:[
    // ---- Section 1: portrait body ----
    {
      properties:{page:{size:{width:12240,height:15840},margin:{top:1300,right:1440,bottom:1300,left:1440}}},
      footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,
        children:[new TextRun({text:"Computational cost of CFD wind-turbine simulations  -  ",size:16,color:GREY}),
                  new TextRun({text:"Page ",size:16,color:GREY}),
                  new TextRun({children:[PageNumber.CURRENT],size:16,color:GREY})]})]})},
      children: bodyPortrait()
    },
    // ---- Section 2: landscape table ----
    {
      properties:{page:{size:{width:12240,height:15840,orientation:PageOrientation.LANDSCAPE},
        margin:{top:900,right:360,bottom:900,left:360}}},
      children:[
        H1("Results - The 24-case grid"),
        P("The table below reports all 24 combinations (6 configurations x 2 turbulence-modelling approaches x 2 turbine sizes). Rows shaded blue are LES (run on the Leonardo Booster GPU partition); rows shaded orange are URANS (run on the DCGP CPU partition). The domain is given in rotor diameters D; \"Flow-throughs\" and \"Rotor revs\" are the simulated physical time expressed, respectively, as domain flow-through times and as rotor revolutions. \"Min cell Δx\" is the smallest cell, in the zone of maximum refinement, in metres and as a fraction of D.",{size:17}),
        grid,
        P("",{}),
        P("Note: every case is run long enough to develop and statistically average the wake, i.e. for several domain flow-through times (6 / 8 / 10 for URANS and 10 / 12 / 14 for LES, at single / 20- / 40-turbine scale), which corresponds to hundreds-to-thousands of rotor revolutions. Partition is implied by the model (LES → Booster GPU, URANS → DCGP CPU). Core-hours are normalised CPU-core-hours; for LES they are mapped to Booster GPU node-hours using 1 node ≈ 600 CPU cores. Energy includes cooling overhead (PUE = 1.2); cost uses 0.15 EUR/kWh.",{size:15,italics:true,color:GREY})
      ]
    },
    // ---- Section 3: portrait, references + back matter ----
    {
      properties:{page:{size:{width:12240,height:15840},margin:{top:1300,right:1440,bottom:1300,left:1440}}},
      children: backPortrait()
    }
  ]
});

function bodyPortrait(){
  const c = [];
  c.push(new Paragraph({spacing:{after:60},children:[new TextRun({text:"Computational Cost of CFD Simulations for Wind Turbines and Wind Farms",bold:true,size:36,color:NAVY})]}));
  c.push(new Paragraph({spacing:{after:40},children:[new TextRun({text:"Grid size, HPC core-hours, runtime on Leonardo (CINECA) and energy cost for 24 scenarios",size:22,color:GREY})]}));
  c.push(new Paragraph({spacing:{after:240},children:[new TextRun({text:"Bibliographic estimate — June 2026",size:18,italics:true,color:GREY})]}));

  c.push(H1("1. Executive summary"));
  c.push(P("This report estimates the grid size, the high-performance-computing (HPC) workload (core-hours), the expected wall-clock time on a CINECA Leonardo-class system, and the corresponding electricity cost (including cooling) for 24 wind-energy CFD scenarios. The scenarios combine six geometrical configurations (single turbine and 20- or 40-turbine farms, each modelled either with fully blade-resolved geometry or with an actuator line/disk representation), two turbulence-modelling strategies (LES and URANS, both embedded in an atmospheric boundary layer, ABL), and two turbine sizes (the NREL 5 MW and the IEA 15 MW reference turbines)."));
  c.push(P("All cases are required to reproduce the wake, not merely the rotor loads, so every simulation is run for several domain flow-through times. Anchored to peer-reviewed studies from the last decade, the headline conclusion is that cost then spans more than six orders of magnitude across the matrix: from about 40,000 core-hours and a few tens of euros for an actuator-model simulation of a single turbine, to roughly 46 billion core-hours and about €34 million for a fully blade-resolved LES of a 40-turbine 15 MW farm — a workload beyond the reach of any existing or near-term HPC system."));

  c.push(H1("2. Scenario definition"));
  c.push(P("Each case is one single simulation, at one single wind speed, in a neutrally-stratified atmospheric boundary layer (no isolated-rotor / uniform-inflow cases). The three axes of the matrix are:"));
  c.push(bullet([R("Configuration (6): ",{bold:true}),R("(1) single turbine, full geometry; (2) single turbine, actuator line/disk; (3) 20-turbine farm, full geometry; (4) 40-turbine farm, full geometry; (5) 20-turbine farm, actuator line/disk; (6) 40-turbine farm, actuator line/disk.")]));
  c.push(bullet([R("Turbulence model (2): ",{bold:true}),R("LES with ABL, and URANS with ABL.")]));
  c.push(bullet([R("Turbine size (2): ",{bold:true}),R("NREL 5 MW (rotor diameter D ≈ 126 m) and IEA 15 MW (D ≈ 240 m).")]));
  c.push(P("6 × 2 × 2 = 24 cases. The full grid of results is in Section 5 (landscape) and in the companion spreadsheet."));

  c.push(H1("3. Methodology and assumptions"));
  c.push(H2("3.1 Mesh sizing"));
  c.push(P("Cell counts are built bottom-up as (number of turbines) × (cells per turbine) + (background ABL/domain mesh). The per-turbine values reflect published practice:"));
  c.push(bullet([R("Full-geometry (blade-resolved): ",{bold:true}),R("URANS rotors require ~50–60 M cells to resolve the blade boundary layers; published blade-resolved URANS of the NREL 5 MW use ~55 M cells [1,2]. Blade-resolved LES embedded in the ABL is far finer — hundreds of millions to billions of cells per rotor; the ExaWind demonstrations of the NREL 5 MW reached up to ~6 billion grid points [3,4]. We adopt 60 M (URANS) and 350 M (LES) cells per turbine for the 5 MW baseline.")]));
  c.push(bullet([R("Actuator line/disk: ",{bold:true}),R("the rotor is represented by body forces, so no blade boundary layer is meshed. Refinement is set by the rotor-disk region (typically tens of cells across D) plus wake refinement [7,8,9,13]. We adopt 6 M (URANS) and 15 M (LES) cells per turbine for the 5 MW baseline.")]));
  c.push(bullet([R("Background ABL mesh: ",{bold:true}),R("a precursor/concurrent-precursor domain is added (4–40 M for a single turbine up to 200–350 M for a 40-turbine farm), consistent with SOWFA-type wind-farm meshes that reach up to ~1 billion cells [10,11,12].")]));
  c.push(P("Turbine size enters through a multiplier on the per-turbine cells (×1.8 for blade-resolved, ×1.4 for actuator models when going from 5 MW to 15 MW), reflecting the larger rotor, higher Reynolds number and larger domain of the IEA 15 MW machine."));
  c.push(P("The computational domain (column \"Domain (in D)\" in the results table) is sized in rotor diameters and scales with the turbine: 24×8×6 D for a single turbine, 44×26×6 D for the 20-turbine farm and 64×32×6 D for the 40-turbine farm (streamwise × lateral × vertical). The streamwise extent leaves several diameters upstream and a long wake-recovery fetch downstream; the vertical extent (~6 D) represents the resolved ABL. For the two turbine sizes this corresponds to domains from about 3.0×1.0×0.8 km (single 5 MW) up to about 15.4×7.7×1.4 km (40-turbine 15 MW farm). The outer domain is identical for the full-geometry and actuator variants of a given configuration — only the near-rotor refinement differs."));

  c.push(H2("3.2 Physical time, time step and wake convergence"));
  c.push(P("The number of time steps is derived as N_steps = T_sim / Δt, where T_sim is the physical simulated time and Δt the time step. Because the objective is to reproduce the wake (not merely the rotor loads), every case — blade-resolved and actuator alike — is run long enough for the flow to develop and be statistically averaged across the domain, i.e. for several flow-through times (hub-height inflow assumed at 10 m/s; rotor speed 12 rpm for the 5 MW and 7.5 rpm for the 15 MW):"));
  c.push(bullet([R("Flow-through times for wake convergence: ",{bold:true}),R("we adopt 6 / 8 / 10 for URANS and 10 / 12 / 14 for LES, for the single / 20- / 40-turbine domains respectively. For every case this corresponds to hundreds-to-thousands of rotor revolutions (reported per case in Section 5).")]));
  c.push(bullet([R("Time step: ",{bold:true}),R("2° of rotor azimuth per step for blade-resolved URANS; ≈1×10⁻⁴ s (CFL-limited on the near-wall cells) for blade-resolved LES; and, for actuator models, the blade tip advancing no more than one finest cell per step (Δt = Δx_min / V_tip).")]));
  c.push(P("The crucial point is that the simulated physical time (set by the wake) is the same for the blade-resolved and actuator versions of a configuration, but the blade-resolved time step is far smaller — fixed by the near-wall CFL limit rather than the rotor-disk resolution. Requiring the wake therefore makes the blade-resolved cases, and especially blade-resolved LES, enormously expensive: a blade-resolved LES of a multi-turbine farm needs O(10⁸) time steps on a multi-billion-cell mesh, which is the single dominant cost in the whole matrix [3,4,7]."));

  c.push(H2("3.3 Solver cost and conversion to core-hours"));
  c.push(P("Core-hours are computed as cells × time steps × C / 3600, where C is the solver cost in core-seconds per cell per time step. For URANS, C ≈ 2×10⁻⁴ is calibrated against a blade-resolved literature reference run of ~16,300 CPU-hours for 55 M cells over ~5,400 steps [JoP CS, 1618:052007] (our calibrated C reproduces ~16,500 CPU-hours for that 55 M-cell, 5,400-step run). For LES we use a lower C ≈ 3×10⁻⁵, reflecting the cheaper explicit/PISO update per cell and calibrated so that a fully-converged actuator-LES farm falls within the published \"days-to-weeks on O(10³–10⁴) cores\" range. These values implicitly fold in parallel inefficiency at scale and should be read as order-of-magnitude engineering estimates, not precise benchmarks."));

  c.push(H2("3.4 Hardware: Leonardo (CINECA)"));
  c.push(P("Leonardo is a ~250 PFlop/s pre-exascale system at CINECA (Bologna). Its Booster partition has 3,456 nodes, each with 4 × NVIDIA A100 (64 GB) GPUs plus a 32-core Intel Ice Lake CPU; its Data-Centric (DCGP) partition has 1,536 nodes, each with 2 × 56-core Intel Xeon 8480+ (Sapphire Rapids) CPUs [14,15]. URANS cases are costed on DCGP (112 cores/node, ~1.1 kW/node); LES cases on the Booster GPU partition (~2.5 kW/node), mapping CPU-core-hours to GPU node-hours with 1 Booster node ≈ 600 CPU cores for finite-volume CFD. Wall-clock times assume representative job sizes: 16 DCGP nodes (single) / 64 DCGP nodes (farm) for URANS; 64 Booster nodes (single blade-resolved), 256 Booster nodes (farm blade-resolved) and 32 Booster nodes (actuator-model LES)."));

  c.push(H2("3.5 Energy and cost"));
  c.push(P("Energy = node-hours × node power × PUE, with PUE = 1.2 (an efficient HPC datacentre, cooling included). Electricity is priced at 0.15 EUR/kWh (EU large-consumer / wholesale band). Cost = energy × price. These figures cover only the compute energy of the production run; they exclude mesh generation, pre/post-processing, failed runs and embodied energy."));

  c.push(H2("3.6 Minimum cell size in the maximum-refinement zone"));
  c.push(P("Because the mesh is strongly graded, the meaningful resolution is the smallest cell, located where the grid is finest. The two modelling families refine fundamentally different things — made explicit by the last three columns of the results table (rotor diameter D, the minimum cell size Δx in metres, and Δx normalised by D):"));
  c.push(bullet([R("Full geometry (blade-resolved): ",{bold:true}),R("the finest cell is the first wall-normal layer on the blade, sized for y+ ≈ 1 to resolve the boundary layer. At the chord Reynolds numbers of these rotors (O(10^7)) this is of order 10^-5 m — tens of micrometres (we adopt 1×10⁻⁵ m for LES and 2×10⁻⁵ m for URANS). Relative to the rotor this is of order 10⁻⁷–10⁻⁸ diameters, which is the physical reason blade-resolved meshes reach hundreds of millions to billions of cells [1,2,3].")]));
  c.push(bullet([R("Actuator line/disk: ",{bold:true}),R("no blade boundary layer is meshed, so the finest cell is set by the rotor-disk / near-wake refinement box. Good practice is a few tens of cells across the rotor and a Gaussian smearing width ε ≈ 2 cells; we adopt Δx ≈ D/100 for LES and ≈ D/64 for URANS — roughly 1–4 m for the two turbine sizes, consistent with SOWFA-type meshes that refine to ~0.3 m near the rotor [9,10,13].")]));
  c.push(P("The absolute (m) and normalised (Δx/D) minimum-cell values are reported per case in Section 5 and in the companion spreadsheet."));

  c.push(H2("3.7 Wind-farm layout and turbine positioning"));
  c.push(P("The cost model treats a farm as N identical turbines plus a shared background domain; it does not place each rotor at explicit coordinates. The geometry enters implicitly, through the domain extent and the number of flow-through times. The domain sizes used in Section 3.1 are consistent with an aligned rectangular array, with the wind blowing along the columns:"));
  c.push(bullet([R("Wind farm 20: ",{bold:true}),R("a 5 × 4 array (5 columns streamwise × 4 rows laterally).")]));
  c.push(bullet([R("Wind farm 40: ",{bold:true}),R("an 8 × 5 array.")]));
  c.push(bullet([R("Spacing: ",{bold:true}),R("≈7 D streamwise (Sx) and ≈5 D laterally (Sy) — the conventional offshore range — with ≈6 D of upstream margin, ≈10–15 D of downstream wake-recovery fetch, and ≈5 D of lateral margin on each side. This reproduces the 44×26×6 D (farm 20) and 64×32×6 D (farm 40) domains.")]));
  c.push(P("Two assumptions follow. First, a single wind direction aligned with the array is assumed — the most demanding case for wake interaction; a staggered layout, a different spacing, or a full wind-rose would change both the domain size and the number of flow-through times, and therefore the cost. Second, because the turbines are treated as identical units, the model does not capture the reduced loading and power of the waked downstream rows; this affects the physical result but not the computational cost, which is what this report estimates. The layout and spacing assumed for each case are listed explicitly in the Assumptions sheet and the per-case columns of the companion spreadsheet."));

  c.push(H1("4. Discussion of the results"));
  c.push(P("Reading the matrix in Section 5, several robust trends emerge. Because every case now resolves the wake over the same number of flow-through times, the comparison across methods is genuinely like-for-like."));
  c.push(bullet([R("Full geometry vs actuator is the dominant lever. ",{bold:true}),R("Resolving the blade boundary layer over a full wake-development time costs about 8× more for URANS (≈39M vs ≈5M core-hours for a 40-turbine 5 MW farm) and three-to-four orders of magnitude more for LES (≈13.5 billion vs ≈5.6M core-hours), because the blade-resolved mesh is far larger and its time step far smaller.")]));
  c.push(bullet([R("LES vs URANS is the second lever. ",{bold:true}),R("For blade-resolved geometry, LES costs roughly 10²–10³× its URANS counterpart (≈98M vs ≈0.23M core-hours for a single 5 MW turbine), driven by the ~300× smaller time step; for actuator models the two are within a factor of a few.")]));
  c.push(bullet([R("Farm size ",{bold:true}),R("scales roughly linearly in the actuator cases (20 → 40 turbines about doubles the cost) and somewhat super-linearly for blade-resolved farms, through the larger shared background domain and a longer flow-through time.")]));
  c.push(bullet([R("Turbine size (5 → 15 MW) ",{bold:true}),R("raises cost by ≈1.3–1.6× for actuator models and ≈2–3× for blade-resolved, through the larger rotor, higher Reynolds number, larger domain and longer flow-through time.")]));
  c.push(bullet([R("Hardware matters as much as the model. ",{bold:true}),R("Because URANS runs on CPU (DCGP) and LES on the energy-efficient A100 GPU partition, a CPU-based actuator URANS can consume as much or more energy than a GPU-based actuator LES of the same farm (≈€8.8k vs ≈€4.2k for the 40-turbine 5 MW farm). \"Cheaper turbulence model\" does not automatically mean \"cheaper simulation\".")]));
  c.push(P("Practically, once the wake must be resolved: actuator-model runs remain affordable — tens of euros for a single turbine up to ≈€14k and a few weeks of wall-clock for a 40-turbine farm. Blade-resolved URANS rises to ≈0.23M–84M core-hours (≈€0.4k–€148k, from days up to ~16 months of wall-clock). Blade-resolved LES of farms is the extreme: ≈13–46 billion core-hours, 10⁵-MWh-scale energy (≈68,000–229,000 MWh) and ≈€10–34 million, with wall-clock measured in years-to-decades on hundreds of GPU nodes — categorically infeasible on any current or near-term system. The practical conclusion is that wake-resolving studies of wind farms must use actuator models, with blade-resolved LES reserved for single rotors or very short single-turbine wake segments."));
  return c;
}

function backPortrait(){
  const c = [];
  c.push(H1("6. Limitations"));
  c.push(P("These are bibliographically-grounded order-of-magnitude estimates, not benchmark measurements. Real costs depend strongly on the specific code (OpenFOAM/SOWFA, Nalu-Wind/AMR-Wind, ANSYS Fluent, lattice-Boltzmann solvers, etc.), numerical scheme, near-wall treatment (wall-resolved vs wall-modelled LES), parallel efficiency, the chosen averaging window, and the actual wind condition. Mesh-independence requirements alone can move blade-resolved cell counts by a factor of several. The GPU-to-CPU equivalence (1 node ≈ 600 cores) is solver-dependent and could vary by 2–3×. The cost matrix should therefore be used to compare scenarios against one another, and to size an allocation request, rather than as a precise forecast of a specific run."));

  c.push(H1("7. References"));
  c.push(P("Peer-reviewed and primary sources, predominantly 2014–2024. (The underlying NREL 5 MW and IEA 15 MW reference-turbine definitions — Jonkman et al. 2009 and Gaertner et al. 2020 — are the standard machine definitions used throughout the wind-energy literature cited below.)",{size:18,italics:true,color:GREY}));
  refs.forEach((r,i)=>c.push(ref(i+1,r[0],r[1])));
  return c;
}

Packer.toBuffer(doc).then(buf=>{fs.writeFileSync("Wind_CFD_Computational_Cost_Report.docx",buf);console.log("written");});
