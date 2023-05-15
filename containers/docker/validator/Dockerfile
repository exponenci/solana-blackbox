ARG GENESIS_HOSTNAME=127.0.0.1
ARG GOSSIP_PORT=8001
ARG RPC_PORT=8899
ARG LOG_PATH=/mnt/logs/solana_validator_node.log

FROM solana-base

ARG GENESIS_HOSTNAME
ARG GOSSIP_PORT
ARG RPC_PORT
ARG LOG_PATH

RUN ./multinode-demo/setup.sh && \
    RUST_LOG='trace' ./multinode-demo/validator.sh \
    --entrypoint $GENESIS_HOSTNAME:$GOSSIP_PORT \
    --rpc-port $RPC_PORT \
    --log $LOG_PATH
