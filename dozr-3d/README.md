# Dozr — doseur à poudre imprimable en 3D

Forme calquée sur les vues de référence et le croquis de profil : entonnoir en **bol conique** (paroi presque verticale en haut qui s'arrondit en se resserrant jusqu'au tube), cannelé (côtes bombées,
rainures fines, bandeau lisse sous la lèvre arrondie), fond en pente directe vers le trou (**pas de grille**), **tube de 10 mm
qui rentre dans le goulot** d'une bouteille standard, manche plat avec pilule noire en creux, bouton
rond noir côté entonnoir, logo **DOZR®** gravé en creux sur le manche et trou de suspension chanfreiné.

L'entonnoir et le manche forment **une seule pièce** : aucun joint visible dessus ni sur les côtés.

![aperçu](apercu.png)

## Fichiers

| Fichier | Contenu | Couleur |
|---|---|---|
| `stl/1_corps_entonnoir_manche.stl` | Entonnoir + manche d'un seul bloc (imprimé debout, dessous à plat) | gris |
| `stl/2_couvercle_bec.stl` | Fond du canal + tube Ø20 × 10 mm (imprimé face plate sur le plateau) | gris |
| `stl/3_clapet_complet.stl` | **Clapet d'une seule pièce** : languette qui ferme le tube + semelle noire visible dans la fenêtre + bouton | noir |
| `dozr_assemblage.3mf` / `.glb` / `.stl` | Vue assemblée en couleurs | |
| `coupe_clapet.png` | Coupe clapet fermé / ouvert | |
| `fonts/Inter-BlackItalic.otf` | Police du logo (Inter, licence SIL OFL 1.1) | |
| `dozr.py` | Source paramétrique : modifier les cotes en tête de fichier puis `python3 dozr.py` | |

## Clapet

![coupe](coupe_clapet.png)

Une seule pièce noire coulisse dans le manche : sa languette passe entre l'entonnoir et le tube,
sa semelle noire apparaît au fond de la fenêtre du manche et seul le bouton rond dépasse.

- Bouton côté entonnoir : la languette couvre tout le tube → **fermé**
- Bouton tiré de 18 mm vers le bout du manche : la languette dégage tout le tube → **ouvert**, la poudre tombe directement

## Dimensions

Proportions relevées sur la vue de face, à l'échelle manche = 30 mm :

- Longueur totale 160 mm, manche 30 × 9 mm
- Entonnoir en bol conique Ø55 en haut → Ø26 au départ du tube, hauteur 32 mm, 48 côtes (`BOWL` dans `dozr.py` : 0 = cône droit, 1 = bol rond)
- Tube Ø20 → Ø19,2, longueur 10 mm, passage Ø14 : rentre dans les goulots standard (passage ~21,7 mm)
- Fond intérieur conique à 50° jusqu'au trou Ø14 : la poudre tombe directement dès que le clapet s'ouvre
- Logo « DOZR® » gravé 0,8 mm, hauteur 6 mm, lisible du bout du manche vers l'entonnoir (`LOGO_*` dans `dozr.py`)
- Fenêtre du clapet 17,3 × 49 mm, bouton Ø16,2, trou de suspension Ø6 (chanfrein Ø8,5)
- Bouton côté entonnoir = **fermé** ; tiré de 18 mm vers le bout du manche = **ouvert**

## Impression

- PETG (contact alimentaire) ou PLA, buse 0,4, couches 0,2 mm, **aucun support**
- Clapet en filament noir, corps et couvercle en gris
- Logo : pour l'avoir noir comme sur le visuel, passer un feutre ou de la peinture dans la gravure puis essuyer le dessus
- Jeu de coulissement 0,3 mm par côté (`CLR` dans `dozr.py`), monter à 0,4 si le clapet force

## Assemblage

1. Retourner le corps. Poser le clapet dans le canal par dessous : le bouton sort par la fenêtre du manche, la languette va sous l'entonnoir.
2. Coller le couvercle (avec le tube) dans son logement sous le corps (cyano ou époxy sur le pourtour, **pas dans le canal**).
3. Vérifier que le clapet coulisse librement : bouton côté entonnoir = fermé.
