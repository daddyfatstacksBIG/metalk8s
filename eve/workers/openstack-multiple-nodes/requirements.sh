#!/bin/bash

yum install -y epel-release

PACKAGES=(
    curl
    git
    python36-pip
    unzip
)

yum install -y "${PACKAGES[@]}"

yum clean all

pip3.6 install tox

TERRAFORM_VERSION=0.11.13

curl -O https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip
unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/local/sbin/
rm -f terraform_${TERRAFORM_VERSION}_linux_amd64.zip

sudo -u eve mkdir -p /home/eve/.ssh/
sudo -u eve ssh-keygen -t rsa -b 4096 -N '' -f /home/eve/.ssh/terraform
