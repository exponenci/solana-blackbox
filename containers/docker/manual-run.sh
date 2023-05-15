#!/usr/bin/env bash

# ---------------------------

## building images
# base solana chain builder
docker build --ulimit nofile=1000000:1000000 -t solana-base ./base # use here

# ---------------------------

## network settings
docker network create -d overlay --attachable chains-network

## running containers
docker run \
    --ulimit nofile=1000000:1000000 \
    --name genesis-container \
    --network chains-network \
    -v /mnt/solana/dev/logs:/mnt/logs \
    --hostname genesis_node \
    -p 80:80 \
    -p 8001:8001 \
    -p 8899:8899 \
    -p 9900:9900 \
    -t -d \
    solana-base

docker run \
    --ulimit nofile=1000000:1000000 \
    --name validator-container \
    --network chains-network \
    -v /mnt/solana/dev/logs:/mnt/logs \
    -t -d \
    solana-base

docker run \
    --ulimit nofile=1000000:1000000 \
    --name client-container \
    --network chains-network \
    -v /mnt/solana/dev/logs:/mnt/logs \
    -t -d \
    solana-base

genesis_ip = $(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' genesis-container)
echo "GENESIS IP: $genesis_ip"

docker exec genesis-container bash -c "./multinode-demo/setup.sh && \
    nohup bash -c './multinode-demo/faucet.sh &' && \
    RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
        --enable-rpc-transaction-history --gossip-host genesis_node --log /mnt/logs/solana_genesis_node.txt"

docker exec validator-container bash -c "./multinode-demo/setup.sh && \
    RUST_LOG='trace' ./multinode-demo/validator.sh \
        --entrypoint genesis_node:8001 --rpc-port 8899 --log /mnt/logs/solana_validator.txt"

docker exec client-container bash -c "./multinode-demo/setup.sh && ./multinode-demo/bench-tps.sh \
    --entrypoint genesis_node:8001 --faucet genesis_node:9900  > /mnt/logs/solana_client.txt 2>/mnt/logs/solana_client_stderr.txt"

# ---------------------------

## parsing results
grep 'Average TPS:' -r $CHAIN_LOG_DIR
grep 'drop rate:' -r $CHAIN_LOG_DIR

# ---------------------------

## stopping containers
docker stop genesis-container validator-container client-container
