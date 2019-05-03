@install @ci @local @multinodes
Feature: Cluster expansion
    Scenario: Add one node to the cluster
        Given the Kubernetes API is available
        When we declare a new node on host "node1"
        Then node "node1" is registered in Kubernetes
        When we deploy the node "node1"
        Then node "node1" has the role master
        And node "node1" has the role etcd

