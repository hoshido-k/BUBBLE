FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# 非rootユーザー
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# 基本ツールのインストール
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    wget \
    vim \
    zsh \
    ca-certificates \
    gnupg \
    lsb-release

# Python 3.11のインストール
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# uvのインストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Node.js 20のインストール
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && npm install -g pnpm yarn

# Expo CLIとEAS CLIのインストール
RUN npm install -g expo-cli eas-cli

# Firebase CLIのインストール
RUN npm install -g firebase-tools

# Google Cloud SDKのインストール（オプション）
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-sdk

# Git設定
RUN git config --global --add safe.directory /workspaces/BUBBLE

# クリーンアップ
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ
WORKDIR /workspace

# デフォルトシェルをzshに
ENV SHELL /bin/zsh
