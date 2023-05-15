
FROM rust:1.48

COPY solana /solana

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libssl-dev \
        libudev-dev \
        pkg-config \
        zlib1g-dev \
        llvm \
        clang \
        cmake \
        make \
        libprotobuf-dev \
        protobuf-compiler && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /solana

ENV RUSTFLAGS="-C target-feature=+avx,+avx2 ${RUSTFLAGS}" \
    TOML_CONFIG=/solana/config.toml \
    NDEBUG=1

RUN rustup --version; \
    cargo --version; \
    rustc --version; \
    cargo build --release --all

RUN $(command -v solana-sys-tuner) --user $(whoami) > sys-tuner.log 2>&1 &

# updating system ulimit for nofile
RUN echo "fs.file-max = 1000000" >> /etc/sysctl.conf
RUN sysctl -p
RUN sed -i '$ d' /etc/security/limits.conf
RUN echo "* soft nproc 1000000\n* hard nproc 1000001\n* soft nofile 1000000\n* hart nofile 1000001\n\n# End of file\n" > /etc/security/limits.conf
RUN sysctl -w fs.file-max=100000
RUN sysctl fs.file-max

# starting /solana/multinode-demo/setup.sh via provided service settings
RUN echo "\n\
### BEGIN INIT INFO\n\
# Provides:          scriptname\n\
# Required-Start:    $remote_fs $syslog\n\
# Required-Stop:     $remote_fs $syslog\n\
# Short-Description: Start daemon at boot time\n\
# Description:       Enable service provided by daemon.\n\
### END INIT INFO\n\
\n\
[Unit]\n\
Description=Solana Validator\n\
After=network.target\n\
Wants=solana-sys-tuner.service\n\
StartLimitIntervalSec=0\n\
\n\
[Service]\n\
Type=simple\n\
Restart=always\n\
RestartSec=1\n\
User=$(whoami)\n\
LimitNOFILE=1000000\n\
LogRateLimitIntervalSec=0\n\
Environment=\"PATH=/solana/target/release:/bin:/usr/bin:/home/$(whoami)/.local/share/solana/install/active_release/bin\"\n\
ExecStart=/solana/multinode-demo/setup.sh\n\
\n\
[Install]\n\
WantedBy=multi-user.target\n" >/etc/systemd/system/$(whoami).service

RUN apt-get update && apt-get install -y systemd
RUN systemctl enable --now $(whoami)
RUN chkconfig $(whoami) on

# The next row will set --no-port-check flag when solana-validator will be called
RUN sed -i '/^default_arg\ \-\-require\-tower=*/adefault_arg --no-port-check' multinode-demo/validator.sh && \
    cp -R config ./config_default && \
    rm -rf target/release/build \
           target/release/deps \
           target/release/.fingerprint \
           target/release/*.d  \
           target/release/libsolana_*  \
           target/release/*.rlib  \
           target/release/*.so \
           target/release/cargo-build-bpf \
           target/release/solana-accounts-bench \
           target/release/solana-banking-bench \
           target/release/solana-bench-exchange \
           target/release/solana-bench-streamer \
           target/release/solana-bench-tps \
           target/release/solana-csv-to-validator-infos \
           target/release/solana-dos \
           target/release/solana-install \
           target/release/solana-install-init \
           target/release/solana-ip-address \
           target/release/solana-ip-address-server \
           target/release/solana-net-shaper \
           target/release/solana-poh-bench \
           target/release/solana-ramp-tps \
           target/release/solana-stake-accounts \
           target/release/solana-stake-monitor \
           target/release/solana-stake-o-matic \
           target/release/solana-sys-tuner \
           target/release/solana-tokens \
           target/release/solana-upload-perf \
           target/release/solana-vote-signer \
           target/release/solana-watchtower
