#
# This state is responsible for pulling the service description
# autogenerated from upstream, and optionally expose it via a given method
# (nodeport, load balancer, ingress…)
#


include:
  - .upstream