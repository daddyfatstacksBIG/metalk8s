{# One day this should be transferred from the fileserver #}
{% set pause_image_archive =
    '/srv/scality/metalk8s-2.0/salt/metalk8s/containerd/files/pause-3.1.tar'
%}

include:
  - .installed

Add strace to debug containerd service:
  pkg.installed:
    - name: strace

# Override some unit parameters for containerd service:
#   file.managed:
#     - name: /etc/systemd/system/containerd.service.d/overrides.conf
#     - source: salt://metalk8s/containerd/files/overrides.conf
#     - user: root
#     - group: root
#     - mode: 644
#     - makedirs: true
#     - dir_mode: 750

Run containerd with strace:
  cmd.run:
    - name: /bin/strace -t -f -o /root/test.trace "systemd-run systemctl start containerd"
    - require:
      - pkg: Add strace to debug containerd service
      - pkg: Install containerd

# Start and enable containerd:
#   service.running:
#     - name: containerd
#     - enable: True
#     - require:
#       - pkg: Install containerd

Inject pause image:
  # The `containerd` states require the `cri` module, which requires `crictl`
  cmd.run:
    - name: >-
        ctr -n k8s.io image import \
            --base-name k8s.gcr.io/pause \
            {{ pause_image_archive }}
    - unless: >-
        ctr -n k8s.io image ls -q | grep k8s.gcr.io/pause | grep 3\\.1
    - require:
      - service: Start and enable containerd
