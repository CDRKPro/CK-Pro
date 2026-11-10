# Dozr — doseur à poudre imprimable en 3D

Forme calquée sur les vues de référence (face + 3/4) : entonnoir Ø55 bas à fond très arrondi, cannelé
dehors (jusque sur l'arrondi) et dedans, tamis rond au centre, manche plat 30 mm, pilule noire en creux,
bouton rond noir en relief côté entonnoir, trou de suspension chanfreiné au bout.

![aperçu](apercu.png)

## Fichiers

| Fichier | Contenu | Couleur |
|---|---|---|
| `stl/1_corps_inferieur.stl` | Dessous : fond arrondi, canal de la languette (imprimé à l'envers) | gris |
| `stl/2_corps_superieur_entonnoir.stl` | Entonnoir cannelé + dessus du manche | gris |
| `stl/3_languette.stl` | Languette coulissante qui ferme le bec + tige du bouton | noir |
| `stl/4_bouton.stl` | Bouton rond avec cercle intérieur | noir |
| `stl/5_tamis.stl` | Grille ronde Ø26 (trous 1,2 mm) | gris acier |
| `stl/6_insert_noir.stl` | Pilule noire collée dans le manche | noir |
| `dozr_assemblage.3mf` / `.glb` / `.stl` | Vue assemblée en couleurs | |
| `dozr.py` | Source paramétrique : modifier les cotes en tête de fichier puis `python3 dozr.py` | |

## Dimensions

Relevées sur la vue de face, à l'échelle manche = 30 mm (à ajuster si tu as les vraies cotes) :

- Longueur totale 160,5 mm, manche 30 × 9 mm
- Entonnoir Ø55 × 28 mm, méplat sous le fond Ø28, 52 cannelures
- Pilule noire 17,3 × 49 mm, commence à 38 mm du centre de l'entonnoir
- Bouton Ø16,2 × 5,5 mm avec disque central Ø9
- Trou de suspension Ø6 (chanfrein Ø8,5) à 125 mm
- Tamis Ø26 ; passage de la poudre Ø14
- Fond plat qui se pose sur le goulot (`SPOUT_L = 8` dans `dozr.py` pour ajouter un bec qui rentre dans le goulot)
- Bouton côté entonnoir (comme sur les vues) = **fermé** ; tiré de 18 mm vers le bout du manche = **ouvert**

## Impression

- PETG (contact alimentaire, meilleur glissement) ou PLA, buse 0,4, couches 0,2 mm, **sans supports**
- Sans imprimante multicolore : imprimer les pièces noires en filament noir, le reste en gris
- Le tamis : couches 0,16 mm conseillées pour des barreaux propres
- Jeu de coulissement : 0,3 mm par côté (`CLR` dans `dozr.py`). Si la trappe force, monter à 0,4.

## Assemblage

1. Mettre la languette dans le canal du corps inférieur, tige vers le haut.
2. Insérer 6 tiges Ø2 × 3,5 mm (bouts de filament 1,75 ou trombone) dans les trous d'alignement.
3. Encoller le pourtour du corps inférieur (cyano ou époxy, **pas dans le canal**) et poser le corps supérieur : la tige passe dans la fente.
4. Coller l'insert noir dans la cuvette en pilule du manche.
5. Emmancher le bouton sur la tige (une goutte de colle si le serrage est léger).
6. Poser le tamis dans son logement au fond de l'entonnoir (affleurant, retirable pour le nettoyage).
