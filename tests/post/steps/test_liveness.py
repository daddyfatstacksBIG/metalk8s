import json
import time

import pytest
from pytest_bdd import scenario, then, parsers

from tests import kube_utils


# Scenarios
@scenario('../features/pods_alive.feature', 'List Pods')
def test_list_pods(host):
    pass


@scenario('../features/pods_alive.feature', 'Exec in Pods')
def test_exec_in_pods(host):
    pass


@scenario('../features/pods_alive.feature', 'Expected Pods')
def test_expected_pods(host):
    pass


# Then
@then(parsers.parse(
    "the '{resource}' list should not be "
    "empty in the '{namespace}' namespace"))
def check_resource_list(host, resource, namespace):
    with host.sudo():
        output = host.check_output(
            "kubectl --kubeconfig=/etc/kubernetes/admin.conf "
            "get %s --namespace %s -o custom-columns=:metadata.name",
            resource,
            namespace,
        )

    assert len(output.strip()) > 0, 'No {0} found in namespace {1}'.format(
            resource, namespace)


@then(parsers.parse(
    "we can exec '{command}' in the pod labeled '{label}' "
    "in the '{namespace}' namespace"))
def check_exec(host, k8s_client, command, label, namespace):
    candidates = kube_utils.get_pods(k8s_client, label, namespace=namespace)

    assert len(candidates) == 1, (
        "Expected one (and only one) pod with label {l}, found {f}"
    ).format(l=label, f=len(candidates))

    pod = candidates[0]

    with host.sudo():
        host.check_output(
            'kubectl --kubeconfig=/etc/kubernetes/admin.conf '
            'exec --namespace %s %s %s',
            namespace,
            pod.metadata.name,
            command,
        )
