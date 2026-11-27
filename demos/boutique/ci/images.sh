#!/bin/sh
# Gestion des images entre environnements, commune aux deux pipelines.
# Principe « construire une fois, déployer partout » : les images sont construites UNE fois (branche dev),
# identifiées par la VERSION de leurs sources (empreinte Git de backend, front, kong, postgres), puis promues.
#
#   sh ci/images.sh version              → affiche la version (identique sur dev, accp et prod pour un même code)
#   sh ci/images.sh present [ETIQUETTE]  → code 0 si les 9 images portent cette étiquette dans le registre
#   sh ci/images.sh etiqueter ETIQUETTE  → ajoute ETIQUETTE aux images de la version courante et les pousse
#
# Étiquettes : v-VERSION (construite) · dev, accp, prod (déployée) · accp-VERSION (recette réussie) · prod-VERSION
set -eu
cd "$(dirname "$0")/.."

# Empreinte des seules sources des images : modifier la doc, les scripts ou les manifestes ne change pas la version
VERSION=$(git rev-parse HEAD:./backend HEAD:./front HEAD:./kong HEAD:./postgres | sha1sum | cut -c1-12)
R="${REGISTRE:-}"
IMAGES="front passerelle identite catalogue commandes notifications expedition kong postgres"

case "${1:-}" in
  version)
    echo "$VERSION"
    ;;
  present)
    etiquette="${2:-v-$VERSION}"
    # Vérification par le démon Docker (docker pull) : fonctionne aussi depuis Jenkins conteneurisé
    for i in $IMAGES; do
      if ! docker pull -q "${R}boutique-$i:$etiquette" >/dev/null 2>&1; then
        echo "Image absente du registre : ${R}boutique-$i:$etiquette"
        exit 1
      fi
    done
    echo "Les 9 images ${R}boutique-*:$etiquette sont présentes."
    ;;
  etiqueter)
    for i in $IMAGES; do
      source="${R}boutique-$i:v-$VERSION"
      docker image inspect "$source" >/dev/null 2>&1 || docker pull -q "$source" >/dev/null
      docker tag "$source" "${R}boutique-$i:$2"
      docker push -q "${R}boutique-$i:$2" >/dev/null
    done
    echo "Images v-$VERSION promues : étiquette « $2 »."
    ;;
  *)
    echo "Usage : sh ci/images.sh version | present [ETIQUETTE] | etiqueter ETIQUETTE"
    exit 1
    ;;
esac
