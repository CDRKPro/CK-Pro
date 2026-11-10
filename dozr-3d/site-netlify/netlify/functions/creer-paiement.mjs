// Fonction Netlify : crée une session de paiement Stripe Checkout pour le panier DOZR.
// La clé secrète Stripe reste ici, côté serveur (variable d'environnement STRIPE_SECRET_KEY),
// et les prix sont recalculés côté serveur : le navigateur n'envoie que couleur / pack / quantité.
// Aucune dépendance npm : appel direct de l'API Stripe.

const PRIX = { 1: 890, 2: 1590, 3: 2190 };               // centimes, par pack (identiques à index.html)
const COULEURS = { gris: "Gris", rouge: "Rouge", vert: "Vert", bleu: "Bleu", blanc: "Blanc" };
const SEUIL_LIVRAISON_OFFERTE = 2;                          // nombre de DOZR à partir duquel la livraison est offerte
const LIVRAISON = Number.parseInt(process.env.LIVRAISON_CENTIMES ?? "490", 10);
const PAYS = (process.env.PAYS_LIVRAISON ?? "FR,BE,LU,CH,MC").split(",").map((p) => p.trim()).filter(Boolean);

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });

export default async (req) => {
  if (req.method !== "POST") return json({ erreur: "Méthode non autorisée." }, 405);

  const cle = process.env.STRIPE_SECRET_KEY;
  if (!cle) return json({ erreur: "Paiement non configuré : ajoute STRIPE_SECRET_KEY dans les variables d'environnement Netlify." }, 500);

  let corps;
  try { corps = await req.json(); } catch { return json({ erreur: "Requête invalide." }, 400); }

  const lignes = (Array.isArray(corps?.items) ? corps.items : [])
    .slice(0, 20)
    .map((l) => ({ couleur: String(l?.couleur), pack: Number(l?.pack), qte: Math.floor(Number(l?.qte)) }))
    .filter((l) => COULEURS[l.couleur] && PRIX[l.pack] && l.qte >= 1 && l.qte <= 20);
  if (!lignes.length) return json({ erreur: "Ton panier est vide." }, 400);

  const site = process.env.URL || new URL(req.url).origin;   // URL du site fournie par Netlify
  const unites = lignes.reduce((s, l) => s + l.pack * l.qte, 0);
  const frais = unites >= SEUIL_LIVRAISON_OFFERTE ? 0 : LIVRAISON;

  const p = new URLSearchParams();
  p.append("mode", "payment");
  p.append("locale", "fr");
  p.append("success_url", `${site}/?paiement=ok&session_id={CHECKOUT_SESSION_ID}`);
  p.append("cancel_url", `${site}/?paiement=annule`);
  p.append("billing_address_collection", "auto");
  p.append("phone_number_collection[enabled]", "true");
  PAYS.forEach((pays, i) => p.append(`shipping_address_collection[allowed_countries][${i}]`, pays));

  lignes.forEach((l, i) => {
    const k = `line_items[${i}]`;
    p.append(`${k}[quantity]`, String(l.qte));
    p.append(`${k}[price_data][currency]`, "eur");
    p.append(`${k}[price_data][unit_amount]`, String(PRIX[l.pack]));
    p.append(`${k}[price_data][product_data][name]`, `DOZR ${COULEURS[l.couleur]} — pack x${l.pack}`);
    p.append(`${k}[price_data][product_data][description]`, "Doseur à clapet pour bouteille, clapet noir");
    p.append(`${k}[price_data][product_data][metadata][couleur]`, l.couleur);
    p.append(`${k}[price_data][product_data][metadata][pack]`, String(l.pack));
  });

  const o = "shipping_options[0][shipping_rate_data]";
  p.append(`${o}[type]`, "fixed_amount");
  p.append(`${o}[fixed_amount][amount]`, String(frais));
  p.append(`${o}[fixed_amount][currency]`, "eur");
  p.append(`${o}[display_name]`, frais ? "Livraison standard" : "Livraison offerte");
  p.append(`${o}[delivery_estimate][minimum][unit]`, "business_day");
  p.append(`${o}[delivery_estimate][minimum][value]`, "3");
  p.append(`${o}[delivery_estimate][maximum][unit]`, "business_day");
  p.append(`${o}[delivery_estimate][maximum][value]`, "7");

  p.append("metadata[commande]", lignes.map((l) => `${l.qte}x ${l.couleur} pack${l.pack}`).join(", ").slice(0, 490));
  const SOURCES = ["facebook", "instagram", "tiktok", "snapchat", "google", "pinterest", "youtube", "direct", "autre"];
  p.append("metadata[source]", SOURCES.includes(corps?.source) ? corps.source : "direct");   // pour « Ventes par source »

  const rep = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: { Authorization: `Bearer ${cle}`, "Content-Type": "application/x-www-form-urlencoded" },
    body: p,
  });
  const data = await rep.json().catch(() => ({}));
  if (!rep.ok || !data.url) {
    console.error("Stripe :", data?.error?.message);
    return json({ erreur: "Le paiement n'a pas pu démarrer. Réessaie dans un instant." }, 502);
  }
  return json({ url: data.url });
};

// Appelée par la page en POST sur /api/paiement
export const config = { path: "/api/paiement" };
