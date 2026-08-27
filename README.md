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

- `resume.tex` is the pixel-matched production source for the older canonical
  `resume.pdf`.
- `dhruv_resume.tex` is the editable source for `dhruv_resume.pdf`.
- `edu_resume.tex` is the editable source for `edu_resume.pdf`.
- `altacv.cls` is the production copy of the historical AltaCV v1.1.5 class.
- `overleaf-source/` contains the authentic recovered Overleaf source lineage
  for the older resume. Its resume is corrected to remove the unsupported
  USACO claim and to retain the verified USAAIO result and competition scope.
  Its recovered class has only the duplicate `cvproject` definition removed so
  current LaTeX compilers can build it without errors.
- The production sources remain deliberately updated and pixel-matched; the
  recovered source is preserved separately so those changes are not lost.
- The standard resume removes the HAB Camp entry and adds Residual Controllers.
- The education resume uses general-reader project language, includes NASA Glenn
  HSEI, and does not include Muon Browser.
- Build all three PDFs with:

  ```sh
  nix-shell --pure -p 'texliveSmall.withPackages (ps: with ps; [ fontawesome lato fontaxes mweights xkeyval dashrule ifmtarg tcolorbox tikzfill enumitem ragged2e etoolbox changepage pgf xcolor biblatex multirow tools ])' gnumake --run 'make resumes'
  ```

  Intermediate LaTeX files are written to `.build/`.
