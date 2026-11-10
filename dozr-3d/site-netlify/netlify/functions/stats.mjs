// Fonction Netlify : statistiques de ventes DOZR lues directement dans Stripe.
// Accès protégé par STATS_TOKEN (variable d'environnement) : /stats.html?token=…
// Lecture seule : ne modifie rien dans Stripe.

const NOMS = { gris: "Gris", rouge: "Rouge", vert: "Vert", bleu: "Bleu", blanc: "Blanc" };
const COULEURS = Object.keys(NOMS);
const MAX_PAGES = 20;                                        // 20 × 100 sessions au maximum par requête

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });

function egal(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// metadata.commande est écrite par creer-paiement.mjs : "2x bleu pack1, 1x vert pack3"
function lirePanier(txt) {
  const lignes = [];
  for (const m of String(txt || "").matchAll(/(\d+)x\s+([a-z]+)\s+pack(\d)/g)) {
    lignes.push({ qte: +m[1], couleur: m[2], pack: +m[3] });
  }
  return lignes;
}

export default async (req) => {
  const url = new URL(req.url);
  const attendu = process.env.STATS_TOKEN;
  if (!attendu) return json({ erreur: "STATS_TOKEN n'est pas configuré sur Netlify." }, 500);
  if (!egal(url.searchParams.get("token") || "", attendu)) return json({ erreur: "Accès refusé." }, 401);
  const cle = process.env.STRIPE_SECRET_KEY;
  if (!cle) return json({ erreur: "STRIPE_SECRET_KEY n'est pas configurée sur Netlify." }, 500);

  const days = Math.min(365, Math.max(1, parseInt(url.searchParams.get("days") || "30", 10) || 30));
  const debut = new Date();
  debut.setHours(0, 0, 0, 0);
  debut.setDate(debut.getDate() - (days - 1));
  const depuis = Math.floor(debut.getTime() / 1000);

  // Toutes les sessions Checkout payées de la période
  const sessions = [];
  let apres = null;
  for (let page = 0; page < MAX_PAGES; page++) {
    const q = new URLSearchParams({ limit: "100", status: "complete", "created[gte]": String(depuis) });
    if (apres) q.set("starting_after", apres);
    const r = await fetch(`https://api.stripe.com/v1/checkout/sessions?${q}`, {
      headers: { Authorization: `Bearer ${cle}` },
    });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) {
      console.error("Stripe :", d?.error?.message);
      return json({ erreur: "Lecture Stripe impossible. Vérifie STRIPE_SECRET_KEY." }, 502);
    }
    sessions.push(...(d.data || []).filter((s) => s.payment_status === "paid"));
    if (!d.has_more || !d.data?.length) break;
    apres = d.data[d.data.length - 1].id;
  }

  const jour = (t) => new Date(t * 1000).toLocaleDateString("sv-SE", { timeZone: "Europe/Paris" });
  const daily = [];
  for (let i = 0; i < days; i++) {
    const d = new Date(debut);
    d.setDate(debut.getDate() + i);
    daily.push({ date: d.toLocaleDateString("sv-SE"), revenue: 0, orders: 0 });
  }
  const parJour = Object.fromEntries(daily.map((d) => [d.date, d]));
  const colors = Object.fromEntries(COULEURS.map((c) => [c, 0]));
  const packs = { 1: 0, 2: 0, 3: 0 };
  const countries = {};
  let revenue = 0, units = 0;
  const recent = [];

  for (const s of sessions) {
    const montant = s.amount_total || 0;
    revenue += montant;
    const j = parJour[jour(s.created)];
    if (j) { j.revenue += montant; j.orders += 1; }
    const lignes = lirePanier(s.metadata?.commande);
    for (const l of lignes) {
      if (colors[l.couleur] !== undefined) colors[l.couleur] += l.qte * l.pack;
      if (packs[l.pack] !== undefined) packs[l.pack] += l.qte;
      units += l.qte * l.pack;
    }
    const adresse = s.collected_information?.shipping_details?.address || s.shipping_details?.address || s.customer_details?.address;
    const pays = adresse?.country;
    if (pays) countries[pays] = (countries[pays] || 0) + 1;
    if (recent.length < 12) {
      recent.push({
        date: s.created * 1000,
        amount: montant,
        panier: lignes.map((l) => `${l.qte}× ${NOMS[l.couleur] || l.couleur} pack x${l.pack}`).join(", ") || "—",
        country: pays || "",
      });
    }
  }

  const orders = sessions.length;
  return json({
    days,
    updated: new Date().toISOString(),
    totals: { revenue, orders, aov: orders ? Math.round(revenue / orders) : 0, units },
    daily, colors, packs, countries, recent,
    tronque: sessions.length >= MAX_PAGES * 100,
  });
};

export const config = { path: "/api/stats" };
