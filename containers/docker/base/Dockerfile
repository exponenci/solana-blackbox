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
    NDEBUG=1 \
    PATH="/solana/target/release:${PATH}"

RUN rustup --version; \
    cargo --version; \
    rustc --version;

RUN $(command -v solana-sys-tuner) --user $(whoami) > sys-tuner.log 2>&1 &

RUN sed -i '/^default_arg\ \-\-require\-tower=*/adefault_arg --no-port-check' multinode-demo/validator.sh
RUN multinode-demo/setup.sh
