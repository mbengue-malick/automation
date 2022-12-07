#!/usr/bin/env bash
#title          : kubectl-ctx.sh
#description    : This script extends kubectl with the `ctx` command to switch between contexts
#author         : [ Pierre d'Aviau de Ternay<pierre.daviaudeternay@irt-systemx.fr>, Jorge Sainz Raso <jorge.sainzraso@irt-systemx.fr> ]
#=============================================================================
config=~/.kube/kube-login/config.yaml
k config use-context $1
rc=$?; if [[ $rc != 0 ]]; then return $rc; fi
sed -i "/current_cluster/s/^current_cluster.\+$/current_cluster: $1/" $config
