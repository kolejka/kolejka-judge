#!/bin/bash

function install_package {
    echo "Installing package $1"
    
    cargo clone $1 
    cd $1
    cargo vendor
    
    mkdir .cargo 
    echo "[source.crates-io]" > .cargo/config.toml
    echo "replace-with = 'vendored-sources'" >> .cargo/config.toml
    echo "[source.vendored-sources]" >> .cargo/config.toml
    echo "directory = 'vendor'" >> .cargo/config.toml

    cd ..
}


# Terminate script if directory already exists
# Just in case
set -e
mkdir /tmp/deps
set +e 

cd /tmp/deps 

while [ ! -z "$1" ]; do
    install_package $1
    shift 
done

cd ..
zip -r deps.zip deps

# Cleanup
rm -rf deps 

