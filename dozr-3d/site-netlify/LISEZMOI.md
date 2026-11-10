# Boutique DOZR — mise en ligne sur Netlify avec Stripe

## Contenu du dossier

| Fichier | Rôle |
|---|---|
| `index.html` | **Toute la boutique en un seul fichier** : page, panier, vue 3D (modèle intégré), appel au paiement |
| `netlify/functions/creer-paiement.mjs` | Fonction serveur qui crée le paiement Stripe. Elle garde ta **clé secrète** à l'abri et recalcule les prix (le navigateur n'envoie que couleur / pack / quantité) |
| `stats.html` + `netlify/functions/stats.mjs` + `netlify/functions/suivi.mjs` | **Page DOZR Stats** (même visuel que Solera Stats) : visiteurs en direct, paniers actifs, paiements en cours, visiteurs, pages vues, ajouts au panier, conversion, sources, commandes et chiffre d'affaires |
| `package.json` | Dépendance `@netlify/blobs` (stockage des visites, installé automatiquement par Netlify) |
| `netlify.toml` | Configuration Netlify (site statique + fonctions) |
| `page_source.html`, `construire.py` | Source de `index.html` (pour régénérer après une modification du modèle 3D) |

La clé secrète Stripe ne peut pas être mise dans `index.html` : n'importe quel visiteur pourrait la lire et faire des remboursements ou des paiements à ta place. C'est pour ça que le paiement passe par la petite fonction Netlify.

## Mise en ligne (15 minutes)

1. **Stripe** : crée ton compte sur stripe.com. Dans *Développeurs → Clés API*, copie la **clé secrète** (`sk_test_…` pour tester, `sk_live_…` pour encaisser pour de vrai).
2. **Netlify** : mets ce dossier dans un dépôt GitHub et crée un site Netlify depuis ce dépôt (*Add new site → Import an existing project*), dossier de base : `dozr-3d/site-netlify`.
   Ou en ligne de commande, depuis ce dossier : `npx netlify-cli deploy --prod`.
   ⚠️ Le glisser-déposer (Netlify Drop) ne déploie pas les fonctions : le paiement ne marcherait pas.
3. **Variable d'environnement** : dans Netlify, *Site configuration → Environment variables*, ajoute
   `STRIPE_SECRET_KEY` = ta clé secrète, puis redéploie.
4. **Test** : avec la clé `sk_test_…`, paye avec la carte `4242 4242 4242 4242`, date future, CVC `123`.
   Les commandes apparaissent dans ton tableau de bord Stripe (*Paiements*), avec l'adresse de livraison et le contenu du panier.
5. Quand tout marche, remplace la clé par `sk_live_…` et redéploie.

## Page de statistiques (DOZR Stats)

1. Dans Netlify, ajoute la variable `STATS_TOKEN` = le mot de passe de ta page de stats (long, à garder pour toi).
2. Ouvre `https://ton-site.netlify.app/stats`, entre le mot de passe : il reste mémorisé sur ton téléphone.
   Ajoute la page à l'écran d'accueil pour l'avoir comme une appli. Elle s'actualise toute seule toutes les 30 s.
3. Pour tester sans données : `https://ton-site.netlify.app/stats?demo`.

D'où viennent les chiffres :
- **visites, sources, paniers, paiements commencés** : la boutique les envoie à `/api/suivi` (identifiant de visiteur aléatoire, aucune donnée personnelle) et ils sont rangés dans Netlify Blobs, sans base de données à créer ;
- **commandes et chiffre d'affaires** : lus dans Stripe (paiements réussis), avec la source de la visite enregistrée au moment du paiement ;
- **sources** : détectées via `utm_source` dans tes liens de pub (ex. `?utm_source=tiktok`), les identifiants de clic Facebook / TikTok / Snapchat / Google, ou le site d'origine. Mets toujours `utm_source` dans tes liens de pub pour des chiffres fiables.

Les visites ne sont comptées qu'à partir de la mise en ligne. Pense à mentionner la mesure d'audience dans tes mentions légales.

## Réglages (variables d'environnement facultatives)

| Variable | Défaut | Rôle |
|---|---|---|
| `LIVRAISON_CENTIMES` | `490` | Frais de livraison pour 1 seul DOZR (offerte dès 2). **Garde la même valeur que `LIVRAISON` dans `index.html`** |
| `PAYS_LIVRAISON` | `FR,BE,LU,CH,MC` | Pays où tu livres |

Les prix (8,90 € / 15,90 € / 21,90 €) sont définis à deux endroits qui doivent rester identiques :
`PRIX` dans `index.html` (affichage) et `PRIX` dans `netlify/functions/creer-paiement.mjs` (montant réellement encaissé).

## Avant d'ouvrir la boutique

- Remplace les avis d'exemple et la note « 4,9 · +3 200 sportifs » par de vrais chiffres.
- Vérifie les promesses de la FAQ (contenance, lave-vaisselle, sans BPA) selon le filament utilisé.
- Ajoute tes CGV et mentions légales (obligatoires pour vendre en ligne en France).
- Dans Stripe, active les reçus par e-mail (*Paramètres → E-mails clients*) si tu veux que les clients en reçoivent un.
