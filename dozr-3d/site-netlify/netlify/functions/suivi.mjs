// Fonction Netlify : reçoit les événements de la boutique (visite, panier, paiement commencé)
// et les range dans Netlify Blobs pour la page de statistiques. Aucune donnée personnelle :
// un identifiant de visiteur aléatoire, la source (Facebook, TikTok…) et le contenu du panier.
import { getStore } from "@netlify/blobs";

const DIX_MIN = 10 * 60 * 1000;
const TRENTE_MIN = 30 * 60 * 1000;
const SOURCES = ["facebook", "instagram", "tiktok", "snapchat", "google", "pinterest", "youtube", "direct", "autre"];

const ok = () => new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
const jourParis = (t = Date.now()) => new Date(t).toLocaleDateString("sv-SE", { timeZone: "Europe/Paris" });
const propre = (s, n = 40) => String(s ?? "").replace(/[^\w\-×· .,:€éèàçùâêîôûÉ]/g, "").slice(0, n);

async function lire(store, cle, defaut) {
  return (await store.get(cle, { type: "json" }).catch(() => null)) ?? defaut;
}

export default async (req) => {
  if (req.method !== "POST") return new Response("Méthode non autorisée", { status: 405 });
  let e;
  try { e = await req.json(); } catch { return ok(); }
  const type = String(e?.type || "");
  const v = propre(e?.visiteur, 36);
  if (!v || !["vue", "ping", "panier", "paiement", "paye"].includes(type)) return ok();
  const source = SOURCES.includes(e?.source) ? e.source : "direct";
  const now = Date.now();
  const store = getStore({ name: "dozr-stats", consistency: "strong" });

  // Visiteurs en direct (dernier signe de vie < 10 min)
  const live = await lire(store, "live", {});
  live[v] = now;
  for (const [k, t] of Object.entries(live)) if (now - t > DIX_MIN) delete live[k];
  await store.setJSON("live", live);
  if (type === "ping") return ok();

  // Compteurs du jour
  const cle = `jour:${jourParis(now)}`;
  const j = await lire(store, cle, { views: 0, visitors: {}, cart: 0, checkout: 0, sources: {} });
  if (type === "vue") {
    j.views += 1;
    if (!j.visitors[v]) { j.visitors[v] = 1; j.sources[source] = (j.sources[source] || 0) + 1; }
  }

  // Paniers actifs (30 min)
  const paniers = await lire(store, "paniers", {});
  const attente = await lire(store, "attente", {});
  if (type === "panier") {
    const items = Array.isArray(e?.items) ? e.items.slice(0, 10).map((x) => propre(x, 60)) : [];
    const n = Math.max(0, Math.min(99, parseInt(e?.n, 10) || 0));
    const total = Math.max(0, Math.min(10000, Number(e?.total) || 0));
    if (n > 0) {
      if (e?.ajout) j.cart += 1;                       // un clic sur « Ajouter au panier »
      paniers[v] = { t: now, n, total, items };
    } else delete paniers[v];
  }
  if (type === "paiement") {
    j.checkout += 1;
    attente[v] = { date: new Date(now).toISOString(), total: Math.max(0, Number(e?.total) || 0) };
  }
  if (type === "paye") { delete attente[v]; delete paniers[v]; }
  for (const [k, p] of Object.entries(paniers)) if (now - p.t > TRENTE_MIN) delete paniers[k];
  for (const [k, p] of Object.entries(attente)) if (now - Date.parse(p.date) > TRENTE_MIN) delete attente[k];

  await Promise.all([store.setJSON(cle, j), store.setJSON("paniers", paniers), store.setJSON("attente", attente)]);
  return ok();
};

export const config = { path: "/api/suivi" };
