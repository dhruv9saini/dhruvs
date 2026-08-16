// Shared one-page resume layout. Edit the content in dhruv_resume.typ or
// edu_resume.typ, then run `make resumes` from the repository root.

#set page(
  paper: "us-letter",
  margin: (top: 0.30in, bottom: 0.27in, left: 0.44in, right: 0.44in),
)
#set text(font: "DejaVu Sans", size: 7.2pt, fill: rgb("111827"))
#set par(leading: 7.9pt)

#let ink = rgb("111827")
#let muted = rgb("374151")
#let accent = rgb("1d4ed8")
#let rule = rgb("9ca3af")

#let resume_header() = {
  align(center)[
    #text(size: 15.6pt, weight: "bold", fill: ink, tracking: 0.35pt)[DHRUV SAINI]
    #linebreak()
    #text(size: 7.3pt, fill: muted)[
      #link("https://dhruvs.pages.dev")[dhruvs.pages.dev]
      #h(7pt) | #h(7pt)
      #link("mailto:dhruv9saini@gmail.com")[#text("dhruv9saini@gmail.com")]
    ]
  ]
}

#let section(title) = block(above: 3.3pt, below: 0.8pt, width: 100%)[
  #text(size: 8.25pt, weight: "bold", fill: ink, tracking: 0.25pt)[#title]
  #v(-1.4pt)
  #line(length: 100%, stroke: 0.4pt + rule)
]

#let resume_entry(title, subtitle: none, bullets: ()) = block(
  above: 1.7pt,
  below: 0pt,
  breakable: false,
)[
  #text(size: 7.3pt, weight: "bold", fill: ink)[#title]
  #if subtitle != none {
    linebreak()
    text(size: 6.85pt, style: "italic", fill: muted)[#subtitle]
  }
  #for bullet in bullets {
    grid(
      columns: (7pt, 1fr),
      column-gutter: 1.1pt,
      align: (left, top),
      inset: (top: 0pt, bottom: 0pt),
      text(fill: accent)[•],
      [#bullet],
    )
  }
]
