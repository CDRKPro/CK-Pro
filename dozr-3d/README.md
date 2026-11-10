# Dozr — doseur à poudre imprimable en 3D

Doseur avec entonnoir cannelé, tamis et trappe coulissante commandée par un bouton sur le manche.
Le bec s'emboîte dans un goulot de bouteille standard (passage ~21,7 mm).

![aperçu](apercu.png)

## Fichiers

| Fichier | Contenu |
|---|---|
| `stl/1_corps_inferieur.stl` | Semelle + bec + canal de la trappe (déjà orienté : à l'envers, bec en l'air) |
| `stl/2_corps_superieur_entonnoir.stl` | Entonnoir + dessus du manche avec fenêtre du bouton |
| `stl/3_trappe_coulissante.stl` | Plaque percée Ø13,5 + tige carrée du bouton |
| `stl/4_bouton.stl` | Capuchon du bouton (dôme sur le plateau) |
| `stl/5_tamis.stl` | Grille anti-grumeaux (trous 1,4 mm) |
| `dozr_assemblage.3mf` / `.glb` / `.stl` | Vue assemblée (couleurs dans le 3MF/GLB) |
| `dozr.py` | Source paramétrique : modifier les cotes en tête de fichier puis `python3 dozr.py` |

## Dimensions

- Longueur totale 151 mm, entonnoir Ø60 mm × 40 mm (≈ 60 ml)
- Bec Ø20,5 → 18,8 mm, longueur 12 mm, passage Ø13 mm
- Course de la trappe 15 mm : **bouton vers l'avant = ouvert**, vers l'arrière = fermé

## Impression

- PETG (contact alimentaire, meilleur glissement) ou PLA, buse 0,4, couches 0,2 mm, **sans supports**
- Le tamis : couches 0,16 mm conseillées pour des barreaux propres
- Jeu de coulissement : 0,3 mm par côté (`CLR` dans `dozr.py`). Si la trappe force, monter à 0,4.

## Assemblage

1. Poser le tamis sur l'épaulement au fond de l'entonnoir (il tient en place, retirable pour le nettoyage).
2. Mettre la trappe dans le canal du corps inférieur, tige vers le haut.
3. Insérer 6 tiges Ø2 × 3,5 mm (bouts de filament 1,75, ou trombone) dans les trous d'alignement.
4. Encoller le pourtour du corps inférieur (colle cyano ou époxy, **pas dans le canal**) et poser le corps supérieur : la tige passe dans la fenêtre.
5. Emmancher le bouton sur la tige (une goutte de colle si le serrage est léger).
