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
