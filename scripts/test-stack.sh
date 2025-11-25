#!/usr/bin/bash
set -o pipefail
set -e
set -u

umask 022

check_salud(){
    echo -e "checkeo de salud"
}

check_salud
#implementar