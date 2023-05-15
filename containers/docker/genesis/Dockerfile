ARG GENESIS_HOSTNAME=127.0.0.1
ARG LOG_PATH=/mnt/logs/solana_genesis_node.log

FROM solana-base

ARG GENESIS_HOSTNAME
ARG LOG_PATH

RUN ./multinode-demo/setup.sh

# run in background
RUN nohup ./multinode-demo/faucet.sh &

RUN RUST_LOG='trace' ./multinode-demo/bootstrap-validator.sh \
    --enable-rpc-transaction-history \
    --gossip-host $GENESIS_HOSTNAME \
    --log $LOG_PATH
