{%- from "metalk8s/map.jinja" import metalk8s with context %}

{%- set salt_ip = grains['metalk8s']['control_plane_ip'] -%}
{%- set products = salt.metalk8s.get_products() %}

Configure salt master:
  file.managed:
    - name: /etc/salt/master.d/99-metalk8s.conf
    - source: salt://metalk8s/salt/master/files/master-99-metalk8s.conf.j2
    - user: root
    - group: root
    - mode: '0644'
    - makedirs: true
    - backup: false
    - template: jinja
    - defaults:
        salt_ip: "{{ salt_ip }}"

Configure salt master roots paths:
  file.serialize:
    - name: /etc/salt/master.d/99-metalk8s-roots.conf
    - user: root
    - group: root
    - mode: '0644'
    - formatter: yaml
    - merge_if_exists: True
    - makedirs: true
    - backup: false
    - dataset:
        file_roots:
        {%- for env in products.keys() | sort(attribute='0') %}
          {{ env }}:
            - /srv/scality/{{ env }}/salt
        {%- endfor %}
        pillar_roots:
        {%- for env in products.keys() | sort(attribute='0') %}
          {{ env }}:
            - /srv/scality/{{ env }}/pillar
        {%- endfor %}
