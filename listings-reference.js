/* ════════════════════════════════════════════════════════════════════════════
   LISTINGS MODULE — Charlotte Peterswald / Christie's International Real Estate

   This renders property cards on the Buying page and Home "Featured" section.
   Right now it shows placeholder listings. To go live with real listings from
   AgentBox (Reapit Sales), a developer only needs to implement ONE function:
   fetchListings() — see the clearly marked block below.

   The rest of this file (rendering, field mapping, fallback) is already done.
   ════════════════════════════════════════════════════════════════════════════ */

(function () {

  /* ──────────────────────────────────────────────────────────────────────────
     STEP 1 — THE ONLY PART A DEVELOPER NEEDS TO WRITE.

     Replace the body of fetchListings() with a call to the AgentBox API.
     It must return a Promise resolving to an array of listing objects in the
     shape shown in PLACEHOLDER_LISTINGS below (id, status, price, address,
     suburb, beds, baths, cars, image, url).

     IMPORTANT: the AgentBox API key must NOT live in this file (it is public).
     Put the API call behind a small server endpoint / serverless function and
     have fetchListings() call THAT endpoint. Example:

        async function fetchListings() {
          const res = await fetch('/api/listings');      // your server proxies AgentBox
          const data = await res.json();
          return data.map(mapAgentBoxListing);           // map their fields -> our shape
        }

     A field-mapping helper is stubbed at mapAgentBoxListing() below to make the
     AgentBox → website field translation obvious.
     ────────────────────────────────────────────────────────────────────────── */
  async function fetchListings() {
    // TODO (developer): replace this line with the real API call described above.
    // Returning null tells the site to show the placeholder cards instead.
    return null;
  }

  /* Maps one AgentBox listing object to the shape this site renders.
     Adjust the right-hand side to the actual AgentBox field names from their
     API docs (issued with your API key). Left side must stay as-is. */
  function mapAgentBoxListing(l) {
    return {
      id:      l.id,
      status:  l.status,                     // e.g. "For Sale" | "Auction" | "Sold"
      price:   l.displayPrice || l.priceText, // AgentBox often sends a display string
      address: l.streetAddress,
      suburb:  l.suburb,
      beds:    l.bedrooms,
      baths:   l.bathrooms,
      cars:    l.carSpaces,
      image:   (l.mainImage && l.mainImage.url) || (l.images && l.images[0] && l.images[0].url),
      url:     l.detailsUrl || "contact.html",
    };
  }

  /* ──────────────────────────────────────────────────────────────────────────
     STEP 2 — everything below is DONE. No changes needed to go live.
     ────────────────────────────────────────────────────────────────────────── */

  // Placeholder listings shown until the feed is connected (same shape as live data).
  const PLACEHOLDER_LISTINGS = [
    { id: "p1", status: "Price on application", price: "", address: "Placeholder residence", suburb: "Suburb", beds: null, baths: null, cars: null, image: null, url: "contact.html" },
    { id: "p2", status: "Auction", price: "", address: "Placeholder residence", suburb: "Suburb", beds: null, baths: null, cars: null, image: null, url: "contact.html" },
    { id: "p3", status: "Expressions of interest", price: "", address: "Placeholder residence", suburb: "Suburb", beds: null, baths: null, cars: null, image: null, url: "contact.html" },
  ];

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

  function specLine(l) {
    const bits = [];
    if (l.beds != null) bits.push(l.beds + " bed");
    if (l.baths != null) bits.push(l.baths + " bath");
    if (l.cars != null) bits.push(l.cars + " car");
    return bits.join(" · ");
  }

  function metaLine(l) {
    const price = l.price ? esc(l.price) : esc(l.status || "");
    return esc(l.suburb) + (price ? " · " + price : "");
  }

  function cardHTML(l) {
    const img = l.image
      ? `<div class="im" style="aspect-ratio:4/3"><img src="${esc(l.image)}" alt="${esc(l.address)}"></div>`
      : `<div class="phold" style="aspect-ratio:4/3"><span>Listing photo</span></div>`;
    const spec = specLine(l);
    return `<a class="card rv on" href="${esc(l.url)}">${img}<h3>${esc(l.address)}</h3>`
      + `<div class="meta">${metaLine(l)}</div>`
      + (spec ? `<div class="meta" style="margin-top:2px">${spec}</div>` : "")
      + `</a>`;
  }

  function render(el, listings, limit) {
    const items = (listings && listings.length ? listings : PLACEHOLDER_LISTINGS).slice(0, limit || 3);
    el.innerHTML = items.map(cardHTML).join("");
  }

  async function init() {
    const buyGrid = document.getElementById("listings-grid");     // Buying page
    const homeGrid = document.getElementById("featured-grid");    // Home page (optional)
    if (!buyGrid && !homeGrid) return;

    let listings = null;
    try { listings = await fetchListings(); } catch (e) { console.warn("Listings feed unavailable, showing placeholders.", e); }

    if (buyGrid) render(buyGrid, listings, 6);
    if (homeGrid) render(homeGrid, listings, 2);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
