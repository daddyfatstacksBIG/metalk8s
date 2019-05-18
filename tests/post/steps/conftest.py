# -*- coding: utf-8 -*-
from pytest_bdd import given, parsers

from tests import kube_utils


# Pytest-bdd steps

# Given
@given(parsers.parse("pods with label '{label}' are '{state}'"))
def check_pod_state(host, label, state):
    pods = kube_utils.get_pods(
        host, label, namespace="kube-system", status_phase="Running",
    )

    assert len(pods) > 0, "No {} pod with label '{}' found".format(
        state.lower(), label
    )
