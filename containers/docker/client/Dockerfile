ARG GENESIS_HOSTNAME=127.0.0.1
ARG GOSSIP_PORT=8001
ARG FAUCET_PORT=9900
ARG TX_COUNT=50
ARG DURATION=5

FROM solana-base

ARG GENESIS_HOSTNAME
ARG GOSSIP_PORT
ARG RPC_PORT
ARG TX_COUNT
ARG DURATION

# set result printer & provde args
RUN ./multinode-demo/bench-tps.sh \
    --entrypoint $GENESIS_HOSTNAME:$GOSSIP_PORT \
    --faucet $GENESIS_HOSTNAME:$FAUCET_PORT \
    --tx_count $TX_COUNT \
    --duration $DURATION > bench-tps-stdout.txt 2>bench-tps-stderr.txt
