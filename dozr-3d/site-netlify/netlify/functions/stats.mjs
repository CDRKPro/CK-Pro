// Fonction Netlify : données de la page DOZR Stats (même format que Solera Stats).
// Visites, paniers et paiements commencés : Netlify Blobs (alimentés par /api/suivi).
// Commandes et chiffre d'affaires : Stripe (paiements réussis), en lecture seule.
// Accès : en-tête x-stats-key (ou ?token=) égal à STATS_TOKEN.
import { getStore } from "@netlify/blobs";

const NOMS = { gris: "Gris", rouge: "Rouge", vert: "Vert", bleu: "Bleu", blanc: "Blanc" };
const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" } });

function egal(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}
const jourParis = (t) => new Date(t).toLocaleDateString("sv-SE", { timeZone: "Europe/Paris" });
const lirePanier = (txt) => [...String(txt || "").matchAll(/(\d+)x\s+([a-z]+)\s+pack(\d)/g)].map((m) => ({ qte: +m[1], couleur: m[2], pack: +m[3] }));

export default async (req) => {
  const url = new URL(req.url);
  const attendu = process.env.STATS_TOKEN;
  if (!attendu) return json({ error: "STATS_TOKEN n'est pas configuré sur Netlify." }, 500);
  const fourni = req.headers.get("x-stats-key") || url.searchParams.get("token") || "";
  if (!egal(fourni, attendu)) return json({ error: "Accès refusé." }, 401);

  const nbJours = Math.min(90, Math.max(1, parseInt(url.searchParams.get("days") || "30", 10) || 30));
  const now = Date.now();
  const dates = [];
  for (let i = nbJours - 1; i >= 0; i--) dates.push(jourParis(now - i * 864e5));

  // --- Visites (Netlify Blobs)
  const store = getStore({ name: "dozr-stats", consistency: "strong" });
  const lire = async (cle, defaut) => (await store.get(cle, { type: "json" }).catch(() => null)) ?? defaut;
  const [live, paniers, attente, ...jours] = await Promise.all([
    lire("live", {}), lire("paniers", {}), lire("attente", {}), ...dates.map((d) => lire(`jour:${d}`, null)),
  ]);
  const days = dates.map((date, i) => {
    const j = jours[i] || {};
    return { date, views: j.views || 0, visitors: Object.keys(j.visitors || {}).length, cart: j.cart || 0, checkout: j.checkout || 0,
      sources: j.sources || {}, orders: 0, revenue: 0, orderSources: {}, revenueSources: {} };
  });
  const parDate = Object.fromEntries(days.map((d) => [d.date, d]));

  // --- Commandes (Stripe)
  const orders = [];
  let error;
  const cle = process.env.STRIPE_SECRET_KEY;
  if (!cle) error = "STRIPE_SECRET_KEY n'est pas configurée : les commandes ne s'affichent pas.";
  else {
    const depuis = Math.floor(Date.parse(dates[0] + "T00:00:00+01:00") / 1000) - 3600;
    let apres = null;
    for (let page = 0; page < 10; page++) {
      const q = new URLSearchParams({ limit: "100", status: "complete", "created[gte]": String(depuis) });
      if (apres) q.set("starting_after", apres);
      const r = await fetch(`https://api.stripe.com/v1/checkout/sessions?${q}`, { headers: { Authorization: `Bearer ${cle}` } });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) { error = "Lecture Stripe impossible : vérifie STRIPE_SECRET_KEY."; break; }
      for (const s of d.data || []) {
        if (s.payment_status !== "paid") continue;
        const total = (s.amount_total || 0) / 100;
        const source = s.metadata?.source || "direct";
        const jr = parDate[jourParis(s.created * 1000)];
        if (jr) {
          jr.orders += 1;
          jr.revenue += s.amount_total || 0;
          jr.orderSources[source] = (jr.orderSources[source] || 0) + 1;
          jr.revenueSources[source] = (jr.revenueSources[source] || 0) + (s.amount_total || 0);
        }
        const adr = s.collected_information?.shipping_details || s.shipping_details;
        const nom = (adr?.name || s.customer_details?.name || "").trim();
        const court = nom ? nom.split(/\s+/)[0] + (nom.split(/\s+/)[1] ? " " + nom.split(/\s+/)[1][0] + "." : "") : "";
        orders.push({
          date: new Date(s.created * 1000).toISOString(), total, source,
          name: court || "Client",
          city: adr?.address?.city || s.customer_details?.address?.city || "",
          panier: lirePanier(s.metadata?.commande).map((l) => `${l.qte}× ${NOMS[l.couleur] || l.couleur} pack x${l.pack}`).join(", "),
        });
      }
      if (!d.has_more || !d.data?.length) break;
      apres = d.data[d.data.length - 1].id;
    }
  }

  const carts = Object.values(paniers).filter((p) => now - p.t < 30 * 60 * 1000).sort((a, b) => b.t - a.t);
  const pending = Object.values(attente).filter((p) => now - Date.parse(p.date) < 30 * 60 * 1000);
  return json({
    live: Object.values(live).filter((t) => now - t < 5 * 60 * 1000).length,
    days, orders, carts, pending, ...(error ? { error } : {}),
  });
};

export const config = { path: "/api/stats" };
