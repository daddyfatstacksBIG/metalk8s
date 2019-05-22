import os.path
import logging


SA_PRIVATE_KEY_PATH = "/etc/kubernetes/pki/sa.key"


log = logging.getLogger(__name__)

__virtualname__ = "metalk8s_certs"


def __virtual__():
    return __virtualname__


def _read_sa_private_key():
    # FIXME: we only have access to this file because:
    #   1- Salt master Pod mounts all of /etc/kubernetes
    #   2- Salt master Pod runs on the 'bootstrap' minion, which is, by chance,
    #      also the 'ca' minion, the owner of this key
    # Suggestion: read through https://github.com/saltstack/salt/issues/45882
    if not os.path.isfile(SA_PRIVATE_KEY_PATH):
        log.warn("Missing SA key to share with master node.")
        return {}

    with open(SA_PRIVATE_KEY_PATH, 'r') as key_file:
        key_data = key_file.read()

    return {"sa_private_key": key_data}


def ext_pillar(minion_id, pillar):
    certs = {}

    nodes_info = pillar.get("metalk8s", {}).get("nodes", {})

    if minion_id not in nodes_info:
        log.warn(
            "No information about minion '{}' in K8s API, skipping.".format(
                minion_id
            )
        )
        return {}

    node_info = nodes_info[minion_id]

    if "master" in node_info["roles"]:
        certs.update(_read_sa_private_key())

    return {"metalk8s": {"certs": certs}}
