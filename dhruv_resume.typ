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
    [Built and scaled the PCM, an AI-powered mobile app predicting paper use, to 30,000 students nationwide in over 150 schools],
    [Trained a symbolic regression model with PySR to predict paper consumption based on school demographics],
    [Leading a team of 20 to develop a nonprofit website and iterating on AI model, now helping save 1.7M sheets of paper per year],
    [Received \$30k in grants supporting sustainability impact],
  ),
)

#resume_entry(
  [West Virginia University: SG-REAL Lab],
  subtitle: [GIS/Software Research Intern | Jul 2025–Present],
  bullets: (
    [Created a 3D modeling and flood segmentation pipeline on any power grid to determine which nodes need most investment],
  ),
)

#resume_entry(
  [Dimension],
  subtitle: [Software Engineer Intern | Jun 2025–Sept 2025],
  bullets: (
    [Implemented webhooks to allow external companies to integrate with the enterprise collaboration platform],
    [Led the process to allow Stripe, Vercel, GitHub, and many other hosted bots in channels],
    [Revamped and modernized the UI, completing several refactors that culminated in a 70% reduction of load time],
  ),
)

#resume_entry(
  [University of Washington],
  subtitle: [Quantum Technical Writing Intern | Aug 2024–Sept 2024],
  bullets: (
    [Worked with Prof. Anantram to develop an editing workflow for his book Quantum Mechanics for Scientists and Engineers],
    [Used Python and React to automatically compare textbook versions and allow students to easily select the best version of any paragraph],
    [Accelerated editing time by 15x],
  ),
)

#section("PROJECTS")

#resume_entry(
  [CAD-bench: Benchmarking Language Models on Functional CAD Generation],
  bullets: (
    [Built a benchmark for CAD generation that evaluates whether parts satisfy functional requirements, not just renderability or visual similarity],
    [Executed rigid-body simulations for complex mechanisms such as gearboxes to verify that generated CAD parts function as intended],
    [Accepted to the ICML AIWILD and FAGEN workshops; currently under review at NeurIPS, with #link("https://github.com/CAD-bench/cad-bench")[code available here] and #link("https://cdn.jsdelivr.net/gh/CAD-bench/cad-bench@main/paper/main.pdf")[paper available here]],
  ),
)

#resume_entry(
  [EDA Bench: An Execution-Based Benchmark for Language Model Agents on Functional PCB Construction],
  bullets: (
    [Built a benchmark for PCB generation that evaluates electrical behavior, not just whether generated boards build successfully],
    [Integrated KiCad, routed-connectivity extraction, ERC/DRC checks, ngspice simulation, and external I/O specifications to verify circuit functionality],
    [Accepted to the ICML FAGEN workshop; currently under review at NeurIPS, with #link("https://github.com/EDA-bench/eda-bench")[code available here] and #link("https://cdn.jsdelivr.net/gh/EDA-bench/eda-bench@master/paper/main.pdf")[paper available here]],
  ),
)

#resume_entry(
  [Residual Controllers],
  bullets: (
    [Built and evaluated fixed residual-stream controllers that steer open language models between thinking and direct-answer response modes],
    [On all 30 AIME 2026 problems, a one-step controller entered thinking mode on 30/30 and scored 16/30, versus 1/30 with thinking off and 2/30 with a random control; #link("https://cdn.jsdelivr.net/gh/dhruv9saini/residual-controllers@master/paper/main.pdf")[paper available here]],
  ),
)

#resume_entry(
  [ThinkSwitch: Iterative LoRA Training and Weight Interpolation for Low-Compute Improvement on Specific-Purpose Reasoning Tasks],
  bullets: (
    [Applied weight interpolation and LoRA to iterative distillation and amplification to greatly improve Qwen3-4B AIME score with only \$3 in compute],
    [Awarded 1st place at the Washington State Science and Engineering Fair; #link("https://arxiv.org/abs/2606.01080")[preprint available here]],
  ),
)

#resume_entry(
  [Muon Browser | TypeScript, Electron],
  bullets: (
    [Created a web browser that allows the user to open and browse pages and notes on an infinite canvas],
    [#link("https://github.com/dhruv9saini/muon/")[Available to download and use here]],
  ),
)

#section("AWARDS AND HONORS")

#resume_entry(
  [National Science Bowl],
  subtitle: [Team Captain | 2021–Present],
  bullets: (
    [Founded Bellevue High School’s first science bowl team, winning 1st place at the nationwide virtual competition],
    [Won a fully-funded trip to Washington D.C. for the National Finals],
  ),
)

#resume_entry(
  [Olympiad Awards],
  subtitle: [Various | 2024–Present],
  bullets: (
    [USACO Platinum Rank],
    [USA AI Olympiad National Finalist, Bronze Medal],
  ),
)

#resume_entry(
  [ARC–The American Rocketry Challenge],
  subtitle: [Team Captain | 2025],
  bullets: (
    [Captained a team of five to build a model rocket following specific criteria, qualified for National Finals twice],
  ),
)

#section("EDUCATION")

#resume_entry(
  [Bellevue High School],
  bullets: (
    [36 ACT, 100+ hours of community service, DECA ICDC finalist],
    [President of Programming Club, coach at Tyee MS and Odle MS programming clubs],
  ),
)
