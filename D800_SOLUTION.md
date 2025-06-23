# Guide de résolution des problèmes avec le Nikon D800

Ce document explique comment résoudre les problèmes courants rencontrés avec le Nikon D800.

## 1. Problèmes résolus

### 1.1. Problème des fichiers sans extension

**Problème :** Les photos téléchargées par gphoto2 depuis le D800 n'ont parfois pas d'extension de fichier, ce qui peut perturber le traitement ultérieur.

**Solution mise en place :**
- Utilisation du paramètre `--filename=%f.%C` dans gphoto2 pour forcer l'ajout de l'extension basée sur le type MIME
- Fonction `add_jpg_extension_to_files` améliorée pour détecter et ajouter l'extension .JPG aux fichiers sans extension
- Script `fix_jpg_extensions.py` pour corriger manuellement les fichiers existants

### 1.2. Problème de suppression des photos sur la carte SD

## Problème identifié

Le Nikon D800 ne supporte pas la commande `--delete-all-files` de gphoto2, mais prend en charge la suppression des fichiers individuels avec `--delete-file=<number>`.

Lorsque nous avons essayé d'utiliser `--delete-all-files --recurse`, gphoto2 renvoyait une erreur indiquant que cette fonctionnalité n'était pas supportée par l'appareil photo.

## Solution mise en place

Nous avons créé deux scripts spécifiques pour résoudre ce problème :

1. **d800_delete.py** : Script qui supprime les photos une par une en utilisant `--delete-file=<number>`
2. **diagnose_d800.py** : Script de diagnostic complet pour identifier et tester les problèmes avec le D800

### Fonctionnement de la solution

1. Lorsque des photos sont téléchargées depuis le D800, le script d800_auto_download.py appelle désormais d800_delete.py
2. Le script d800_delete.py :
   - Liste tous les fichiers présents sur la carte SD
   - Les supprime un par un avec la commande `--delete-file=<number>`
   - Gère les erreurs potentielles et libère correctement l'accès USB

### 1.3. Problème des fichiers sans extension sur le serveur FTP

**Problème :** Les photos téléchargées sont correctement renommées localement avec l'extension .JPG, mais cette extension n'est pas préservée lors du transfert FTP.

**Cause :** Le script `lftp_send_jpg.sh` utilise la commande `put "$FILE" -o "$FILENAME"` où `$FILENAME` est simplement le nom de base du fichier, ce qui ne gère pas correctement l'ajout d'extension pour les fichiers qui n'en ont pas initialement.

**Solution mise en place :**
- Script `lftp_send_jpg_fixed.sh` qui :
  1. Détecte les fichiers sans extension et ajoute .JPG pour le transfert FTP
  2. Préserve les extensions existantes
  3. Assure que tous les fichiers ont l'extension .JPG sur le serveur FTP
- Modification de `auto_jpg_transfer.py` pour utiliser ce nouveau script

## Comment utiliser

### Correction des fichiers sans extension

Pour corriger manuellement les fichiers sans extension dans le répertoire de téléchargement:

```bash
python3 /home/server01/projet_ftp/Projet_FTP/fix_jpg_extensions.py
```

Options disponibles:
- `--dry-run` : Simuler sans faire de modifications
- `--force` : Forcer l'ajout de .JPG à tous les fichiers sans extension (même si ce ne sont pas des JPEG)
- `-d /chemin/vers/dossier` : Spécifier un dossier différent de celui configuré

Le script gère les cas suivants:
- Fichiers sans extension (ajout de .JPG)
- Extensions en minuscules (.jpg ou .jpeg → .JPG)
- Vérification du format JPEG en analysant les premiers octets du fichier

### Configuration automatique

La solution pour les fichiers sans extension est automatiquement activée dans le script principal de téléchargement `d800_auto_download.py`. Aucune configuration supplémentaire n'est requise.

### Exécution manuelle

Pour déclencher manuellement la suppression des photos de la carte SD :

```bash
python3 /home/server01/projet_ftp/Projet_FTP/d800_delete.py
```

### Diagnostic

Pour diagnostiquer les problèmes avec le D800 :

```bash
python3 /home/server01/projet_ftp/Projet_FTP/diagnose_d800.py
```

Ce script exécutera une série de tests pour vérifier :
- La détection de l'appareil photo
- Les capacités supportées
- Le téléchargement des fichiers
- La suppression des fichiers

### Correction des problèmes d'extension FTP

Pour tester la solution pour les fichiers sans extension sur le serveur FTP:

```bash
python3 /home/server01/projet_ftp/Projet_FTP/diagnose_d800.py
```

Pour tester spécifiquement le transfert FTP avec et sans la correction:

```bash
/home/server01/projet_ftp/Projet_FTP/test_ftp_extensions.sh
```

Le script de diagnostic montre si le problème est présent dans votre configuration et suggère la correction.

## Améliorations possibles

- Ajouter une vérification des fichiers téléchargés avant la suppression
- Améliorer la gestion des erreurs en cas de déconnexion de l'appareil
- Optimiser la vitesse de suppression en regroupant les commandes

## Notes importantes

- Ne jamais débrancher l'appareil photo pendant les opérations de suppression
- La suppression des fichiers est définitive et ne peut pas être annulée
- En cas de problème, vérifiez les logs dans /home/server01/projet_ftp/Projet_FTP/logs/d800_delete.log
