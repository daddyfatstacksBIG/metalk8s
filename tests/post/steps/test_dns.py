import os

from kubernetes import client, config
import pytest
from pytest_bdd import scenario, then, parsers
import yaml

from tests import utils


@pytest.fixture
def busybox_pod(k8s_client):
    # Create the busybox pod
    pod_manifest = os.path.join(
        os.path.realpath(os.path.dirname(__file__)),
        "files",
        "busybox.yaml"
    )
    with open(pod_manifest, encoding='utf-8') as pod_fd:
        pod_manifest_content = yaml.safe_load(pod_fd)

    k8s_client.create_namespaced_pod(
        body=pod_manifest_content, namespace="default"
    )

    # Wait for the busybox to be ready
    def _check_status():
        pod_info = k8s_client.read_namespaced_pod(
            name="busybox",
            namespace="default",
        )
        assert pod_info.status.phase == "Running", (
            "Wrong status for 'busybox' Pod - found {status}"
        ).format(status=pod_info.status.phase)

    utils.retry(_check_status, times=10)

    yield "busybox"

    # Clean-up resources
    k8s_client.delete_namespaced_pod(
        name="busybox",
        namespace="default",
        body=client.V1DeleteOptions(),
    )


# Scenarios
@scenario('../features/dns_resolution.feature', 'check DNS')
def test_dns(host):
    pass


@then(parsers.parse("the hostname '{hostname}' should be resolved"))
def resolve_hostname(busybox_pod, host, hostname):
    with host.sudo():
        # test dns resolve
        result = host.run(
            "kubectl --kubeconfig=/etc/kubernetes/admin.conf "
            "exec -ti %s nslookup %s",
            busybox_pod,
            hostname,
        )

        assert result.rc == 0, "Cannot resolve {}".format(hostname)
