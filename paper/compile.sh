#!/bin/sh

# Copy figures
#cp ../gen-figures/*/*.pdf figures/

# Add standard EHTC papers bibliography to exported list
#> paper.bib
#cat iharm3d_paper.bib >> paper.bib
#cat EHTC.bib >> paper.bib

podman run --rm \
    --volume $PWD:/data:Z \
    --env JOURNAL=joss \
    openjournals/inara
