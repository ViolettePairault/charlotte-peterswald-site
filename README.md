# Charlotte Peterswald — Christie's International Real Estate NSW

Static marketing site. No build step: plain HTML, CSS and JavaScript.
Deploys as-is to Vercel, Netlify, or any static host.

## Pages

| File | Page |
|---|---|
| `index.html` | Home |
| `selling.html` | Selling (appraisal + cost-of-selling tool) |
| `buying.html` | Buying (listings + investor tools) |
| `management.html` | Property Management (rent appraisal tool) |
| `tools.html` | Tools |
| `contact.html` | Contact |

Supporting files:

- `media/` — hero videos (mp4)
- `assets/` — Christie's brochure PDF
- `listings-reference.js` — reference copy of the listings module, for the developer wiring up the AgentBox feed
- `preview.html` — internal page switcher for local review. Not linked from the site; safe to delete before launch.

Images are base64-embedded in the HTML, so the pages are large but entirely self-contained.

## Forms

All five forms POST to a single Formspree endpoint:

- Sale appraisal
- Rent appraisal
- Investor tool access
- Contact enquiry
- Newsletter subscribe

Each submission is tagged with a `formType` field so they can be told apart.

The endpoint is set once per page:

```js
window.CP_FORM_ENDPOINT = "https://formspree.io/f/mojgwveg";
```

To change where enquiries are delivered, update that line in **every** HTML file, or
change the destination address inside the Formspree dashboard.

If the endpoint is ever blank, forms fail gracefully: the visitor is shown a message
asking them to call, rather than the submission being silently lost.

## Lead unlock

Visitor details entered in any tool are stored in `sessionStorage` under `cp_lead`,
which unlocks the other tools for the rest of that visit. Cleared when the tab closes.

## Listings

The three For Sale cards on `buying.html` are rendered by a small module from a data
array. To connect the live AgentBox (Reapit) feed, implement `fetchListings()` — see
the comments in `listings-reference.js`. The API key must sit behind a server endpoint,
never in this repo.

## Still outstanding

- Listing data is entered by hand until the AgentBox feed is connected
- Suburb medians in the appraisal tools are indicative and should be confirmed
  before launch, or replaced with a live data feed
- Address entry is free-text; Google Places autocomplete is not yet wired in
- Hero videos and several interiors are licensed stock
