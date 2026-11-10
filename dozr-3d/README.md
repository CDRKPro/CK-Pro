# Dozr — doseur à poudre imprimable en 3D

Forme calquée sur les vues de référence : entonnoir **conique vers le bas**, cannelé (côtes bombées,
rainures fines, bandeau lisse sous la lèvre arrondie), tamis rond au centre du fond, **bec de 10 mm
qui rentre dans le goulot** d'une bouteille standard, manche plat avec pilule noire en creux, bouton
rond noir côté entonnoir et trou de suspension chanfreiné.

L'entonnoir et le manche forment **une seule pièce** : aucun joint visible dessus ni sur les côtés.

![aperçu](apercu.png)

## Fichiers

| Fichier | Contenu | Couleur |
|---|---|---|
| `stl/1_corps_entonnoir_manche.stl` | Entonnoir + manche d'un seul bloc (imprimé debout, dessous à plat) | gris |
| `stl/2_couvercle_bec.stl` | Fond du canal + bec Ø20 × 10 mm (imprimé face plate sur le plateau) | gris |
| `stl/3_languette.stl` | Languette coulissante qui ferme le passage, avec la tige du bouton | noir |
| `stl/4_bouton.stl` | Bouton rond Ø16,2 avec disque central | noir |
| `stl/5_tamis.stl` | Grille ronde Ø26 (trous 1,2 mm) | gris acier |
| `stl/6_insert_noir.stl` | Pilule noire de la fente | noir |
| `dozr_assemblage.3mf` / `.glb` / `.stl` | Vue assemblée en couleurs | |
| `dozr.py` | Source paramétrique : modifier les cotes en tête de fichier puis `python3 dozr.py` | |

## Dimensions

Proportions relevées sur la vue de face, à l'échelle manche = 30 mm :

- Longueur totale 160 mm, manche 30 × 9 mm
- Entonnoir conique Ø55 en haut → Ø34 en bas, hauteur 34 mm (≈ 36 ml), 48 côtes
- Bec Ø20 → Ø19,2, longueur 10 mm, passage Ø14 : rentre dans les goulots standard (passage ~21,7 mm)
- Pilule 17,3 × 49 mm, bouton Ø16,2, trou de suspension Ø6 (chanfrein Ø8,5)
- Bouton côté entonnoir = **fermé** ; tiré de 18 mm vers le bout du manche = **ouvert**

## Impression

- PETG (contact alimentaire) ou PLA, buse 0,4, couches 0,2 mm, **aucun support**
- Pièces noires en filament noir, le reste en gris
- Tamis : couches 0,16 mm conseillées
- Jeu de coulissement 0,3 mm par côté (`CLR` dans `dozr.py`), monter à 0,4 si la languette force

## Assemblage

1. Retourner le corps. Glisser la languette dans le canal par dessous, tige vers le haut : elle sort par la fente du manche.
2. Coller le couvercle (avec le bec) dans son logement sous le corps (cyano ou époxy sur le pourtour, **pas dans le canal**).
3. Coller l'insert noir dans la pilule, puis emmancher le bouton sur la tige.
4. Poser le tamis dans son logement au fond de l'entonnoir (affleurant, retirable).
