# Webgency Tilda page — local mirror

Local copy of `https://webgency.tilda.ws/`, downloaded on 21 July 2026.

## Preview

From this directory, run:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000/`.

Use the HTTP-server preview for Tilda's lazy loading, Zero Block animations,
audio controls, and other JavaScript behavior. Opening `index.html` through
`file://` may be restricted by browser module and cross-origin security rules.

## Files

- `index.html` — local entry page with mirrored asset paths
- `original-response.html` — untouched response from the live page
- `assets-mirror/` — Tilda libraries, page bundles, images, SVGs, and audio
- `scripts/download_site.py` — reproducible public-site downloader

The embedded Google Map, outbound links, analytics, and hosted form submission
remain network services. The downloaded page is a compiled Tilda publication,
not the original Tilda editor project.

## Deployment

This folder can be deployed as a static site on GitHub Pages. Publish the
contents of `webgency-tilda/` so `index.html` is at the site root, alongside
the `assets-mirror/` directory.

The RSVP form still depends on Tilda's hosted form backend via the embedded
`data-tilda-formskey`. GitHub Pages can serve the form UI, but it cannot store
submissions by itself. Before relying on it for guests, test one real RSVP on
the deployed GitHub Pages URL. If Tilda rejects submissions from the GitHub
Pages domain, replace the form backend with a static-friendly service such as
Formspree, Getform, Netlify Forms, or a small custom API.
