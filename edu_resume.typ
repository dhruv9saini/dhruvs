#import "resume_template.typ": resume_header, section, resume_entry

#set page(
  paper: "us-letter",
  margin: (top: 0.30in, bottom: 0.27in, left: 0.44in, right: 0.44in),
)
#set text(font: "DejaVu Sans", size: 7.2pt, fill: rgb("111827"))
#set par(leading: 7.9pt)

#resume_header()

#section("EXPERIENCE")

#resume_entry(
  [A Sustainable Future],
  subtitle: [CEO | Oct 2023–Present],
  bullets: (
    [Built PCM, an AI-powered mobile app that helps schools predict paper use, reaching 30,000 students nationwide in over 150 schools.],
    [Trained a model that finds patterns in school data to estimate paper consumption.],
    [Leading a team of 20 to develop a nonprofit website and improve the model; it now helps save 1.7M sheets of paper per year.],
    [Received \$30k in grants supporting sustainability impact.],
  ),
)

#resume_entry(
  [West Virginia University: SG-REAL Lab],
  subtitle: [GIS/Software Research Intern | Jul 2025–Present],
  bullets: (
    [Created a 3D map and flood-detection process for power grids to identify the parts that need investment most.],
  ),
)

#resume_entry(
  [Dimension],
  subtitle: [Software Engineer Intern | Jun 2025–Sept 2025],
  bullets: (
    [Connected the collaboration platform to outside services through webhooks, which automatically share information between apps.],
    [Led support for Stripe, Vercel, GitHub, and many other hosted bots inside channels.],
    [Modernized the interface; the resulting refactors reduced load time by 70%.],
  ),
)

#resume_entry(
  [University of Washington],
  subtitle: [Quantum Technical Writing Intern | Aug 2024–Sept 2024],
  bullets: (
    [Worked with Prof. Anantram on a clearer editing process for his book _Quantum Mechanics for Scientists and Engineers_.],
    [Built Python and React tools that compare textbook drafts and help students choose the best version of any paragraph.],
    [Reduced editing time by 15x.],
  ),
)

#section("PROJECTS")

#resume_entry(
  [CAD-bench: Benchmarking Language Models on Functional CAD Generation],
  bullets: (
    [Built a test suite for AI-generated 3D parts that checks whether a part works as intended, not only whether it looks correct.],
    [Ran physics simulations of mechanisms such as gearboxes to test whether generated parts work in motion.],
    [Accepted to the ICML AIWILD and FAGEN workshops; currently under review at NeurIPS, with #link("https://github.com/CAD-bench/cad-bench")[code available here] and #link("https://cdn.jsdelivr.net/gh/CAD-bench/cad-bench@main/paper/main.pdf")[paper available here].],
  ),
)

#resume_entry(
  [EDA Bench: An Execution-Based Benchmark for Language Model Agents on Functional PCB Construction],
  bullets: (
    [Built a test suite for AI-designed circuit boards that checks electrical behavior, not only whether a design file opens.],
    [Combined KiCad, connection and safety checks, circuit simulation, and real-world input/output requirements to test whether a circuit functions.],
    [Accepted to the ICML FAGEN workshop; currently under review at NeurIPS, with #link("https://github.com/EDA-bench/eda-bench")[code available here] and #link("https://cdn.jsdelivr.net/gh/EDA-bench/eda-bench@master/paper/main.pdf")[paper available here].],
  ),
)

#resume_entry(
  [Residual Controllers],
  bullets: (
    [Studied the small internal signal that tells an open AI model whether to begin step-by-step reasoning or give a direct answer.],
    [On all 30 AIME 2026 problems, a one-time adjustment entered thinking mode on 30/30 and scored 16/30, compared with 1/30 when thinking was off; #link("https://cdn.jsdelivr.net/gh/dhruv9saini/residual-controllers@master/paper/main.pdf")[paper available here].],
  ),
)

#resume_entry(
  [ThinkSwitch: Iterative LoRA Training and Weight Interpolation for Low-Compute Improvement on Specific-Purpose Reasoning Tasks],
  bullets: (
    [Used two low-cost ways to adapt a language model—small trainable additions and blended saved model weights—to improve Qwen3-4B performance on AIME with only \$3 in compute.],
    [Awarded 1st place at the Washington State Science and Engineering Fair; #link("https://arxiv.org/abs/2606.01080")[preprint available here].],
  ),
)

#resume_entry(
  [Muon Browser | TypeScript, Electron],
  bullets: (
    [Created a web browser that lets people place pages and notes on an open, unlimited workspace.],
    [#link("https://github.com/dhruv9saini/muon/")[Available to download and use here].],
  ),
)

#section("AWARDS AND HONORS")

#resume_entry(
  [National Science Bowl],
  subtitle: [Team Captain | 2021–Present],
  bullets: (
    [Founded Bellevue High School’s first science bowl team, winning 1st place at the nationwide virtual competition.],
    [Won a fully-funded trip to Washington, D.C. for the National Finals.],
  ),
)

#resume_entry(
  [Olympiad Awards],
  subtitle: [Various | 2024–Present],
  bullets: (
    [USACO Platinum Rank.],
    [USA AI Olympiad National Finalist, Bronze Medal.],
  ),
)

#resume_entry(
  [ARC–The American Rocketry Challenge],
  subtitle: [Team Captain | 2025],
  bullets: (
    [Captained a team of five to build a model rocket following specific criteria, qualified for National Finals twice.],
  ),
)

#section("EDUCATION")

#resume_entry(
  [Bellevue High School],
  bullets: (
    [36 ACT, 100+ hours of community service, DECA ICDC finalist.],
    [President of Programming Club, coach at Tyee MS and Odle MS programming clubs.],
  ),
)
