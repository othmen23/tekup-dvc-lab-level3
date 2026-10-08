# Niveau 3 : travail d'équipe sur Wine Quality

## Exercice 3.1 : pipeline sur données réelles
- Données brutes versionnées avec `dvc add` (rouge 1599 lignes, blanc 4898 lignes). Sorties intermédiaires non versionnées par Git.
- Étapes : `ingest_clean` (fusion + colonne color, doublons, contrôles) -> `featurize_split` (features, cible quality >= 7, split stratifié) -> `train` -> `evaluate`.
- ingest_clean : 6497 -> 5320 lignes (1177 doublons supprimés). Split : train 4256 / test 1064, 19 % de bons vins.
- Métriques de base : accuracy 0.8374, F1 0.3930 (F1 de la classe "bon", classe minoritaire). Tag `v1.0.0-wine-baseline`.

## Exercice 3.2 : Alice et Bob
- Dépôt central `central/wine.git` (bare) et stockage DVC partagé `central/dvc-storage`.
- Alice (`alice/normalize`) ajoute la normalisation dans `featurize_split.py`, `dvc repro`, push, merge dans main.
- Bob (`bob/dedupe-fix`), sans avoir tiré main, modifie les mêmes lignes (déduplication). Le merge de `origin/main` donne un conflit sur `src/featurize_split.py` et sur `dvc.lock` (metrics.json fusionne sans conflit).
- Résolution : fichier Python fusionné à la main (déduplication puis normalisation) ; `dvc.lock` non fusionné à la main : `dvc repro` l'a régénéré. Puis commit, push, merge dans main, `dvc push`.
- La déduplication de Bob supprime 0 ligne (déjà faite dans `ingest_clean`). La normalisation est calculée avant le split : légère fuite de données, limite assumée.
- Vérification dans un clone neuf : `git clone`, `dvc pull`, `dvc repro` : tout à jour, métriques identiques (accuracy 0.8355, F1 0.3860).

## Exercice 3.3 : régression de métrique
- Commits c1 à c10 sur main. Un premier essai de régression (c4, suppression de la colonne `alcohol`) n'a pas dégradé la métrique ; il est remplacé par une vraie régression en c8 (mélange des lignes de X à l'entraînement, `src/train.py`).
- `dvc metrics diff` : F1 0.396 -> 0.0 (accuracy 0.839 -> 0.809, soit la classe majoritaire).
- `git bisect run bash check.sh` (check.sh = `dvc repro` + `check_metric.py`, seuil F1 >= 0.35) désigne `582003a c8: refactor training input` comme premier mauvais commit.
- `git diff c7 c8 -- dvc.lock` : seuls le md5 de `src/train.py` et celui de `models/model.pkl` changent ; les hashes des données restent identiques : régression de code.
- Correction : `git revert c8`, `dvc repro` (dvc.lock régénéré), F1 revenu à 0.3958. Tag annoté `v1.2.0-regression-fixed`.
- `dvc gc -w -f` (en local, sans `-c`) : cache 6 -> 13 objets après `dvc fetch -A`, puis 13 -> 6 après gc (7 objets supprimés). Les deux copies du remote gardent leurs 13 objets.

## Questions de contrôle

**Pourquoi régénérer `dvc.lock` après résolution est-il plus sûr que fusionner deux dvc.lock à la main ?**
dvc.lock contient les hashes md5 du code, des paramètres et des sorties, qui doivent correspondre aux fichiers réels du commit. Une fusion manuelle mélange des hashes de deux historiques et peut déclarer à tort une étape à jour. `dvc repro` calcule les hashes depuis l'état réel fusionné : le fichier est cohérent par construction.

**Comment distinguer une régression de code d'une régression de données grâce à dvc.lock ?**
On compare dvc.lock entre le bon et le mauvais commit. Si seul le hash d'une dépendance de code (.py) change, c'est une régression de code (cas de c7 -> c8 : `src/train.py`). Si le hash d'une dépendance de données change (par exemple `wine_clean.csv` ou un fichier `.dvc` brut) alors que le code est identique, c'est une régression de données.

**Pourquoi `dvc gc` est-il risqué sur un remote partagé sans les bons drapeaux ?**
`dvc gc -w` supprime tout objet que le workspace courant ne référence pas. Avec `-c`, la suppression touche le stockage partagé : les branches et tags des collègues (par exemple `v1.0.0-wine-baseline`) perdent leurs données, sans retour possible. Dans le test local, `dvc gc -w -f` a supprimé 7 objets du cache et laissé les remotes intacts. Sur un remote partagé, on utilise `-A` (tout ce que référencent les branches et tags) et on se met d'accord avec l'équipe avant tout `-c`.
