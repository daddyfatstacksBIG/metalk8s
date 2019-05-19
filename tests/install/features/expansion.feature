@install @ci @local @multinodes
Feature: Cluster expansion
    Scenario: Add one node to the cluster
        Given the Kubernetes API is available
        When we declare a new "control-plane" node on host "node1"
        Then node "node1" is registered in Kubernetes
        When we deploy the node "node1"
        Then we have 1 running pod labeled 'component=kube-controller-manager' on node 'node1'
        And we have 1 running pod labeled 'component=kube-scheduler' on node 'node1'
        And we have 1 running pod labeled 'component=kube-apiserver' on node 'node1'
        And we have 1 running pod labeled 'component=etcd' on node 'node1'
        And node "node1" is a member of etcd cluster

