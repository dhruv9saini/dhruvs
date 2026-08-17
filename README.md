# dhruvs

Static personal site deployed at `https://dhruvs.pages.dev/`.

## Routes

- `/` is the public homepage.
- Event contact pages may be unlisted. Keep those routes out of public
  navigation, sitemaps, and robots.txt so they are only available to people who
  already have the URL. Add `noindex,nofollow` metadata and matching Pages
  headers for the route and any attached assets.
- Event contact pages should match the homepage's simple list style and use
  concise labeled links, for example `Website: dhruvs.pages.dev`.
- `sitemap.xml` lists only public routes. Do not add unlisted event routes
  there.

## ICML QR

QR codes for event contact pages should use the `dhruvs.pages.dev` deployment
domain, not a preview or alternate host.

## Resume PDFs

- `dhruv_resume.tex` is the editable source for `dhruv_resume.pdf`.
- `edu_resume.tex` is the editable source for `edu_resume.pdf`.
- `altacv.cls` is a vendored historical AltaCV v1.1.5 class. It preserves the
  legacy FontAwesome and Lato-based design used by the canonical original PDF.
- The original TeX source was unavailable. The LaTeX sources were reconstructed
  against the canonical original PDF and then updated deliberately.
- The standard resume removes the HAB Camp entry and adds Residual Controllers.
- The education resume uses general-reader project language, includes NASA Glenn
  HSEI, and does not include Muon Browser.
- Build both PDFs with:

  ```sh
  nix-shell --pure -p 'texliveSmall.withPackages (ps: with ps; [ fontawesome lato fontaxes mweights xkeyval dashrule ifmtarg tcolorbox tikzfill enumitem ragged2e etoolbox changepage pgf xcolor biblatex multirow tools ])' gnumake --run 'make resumes'
  ```

  Intermediate LaTeX files are written to `.build/`.
