---
title: CodingBook：从0到1建设一个WSL Ubuntu系统
date: "2025-01-25"
draft: false
tags: ["工具", "操作系统", "WSL", "Ubuntu", "Docker"]
categories: ["环境配置","操作系统"]
description: "记录从头搭建WSL UBUNTU系统的过程，避免重复踩坑"
---




# README: WSL2 + Ubuntu 22.04 + GPU + Docker + Proxy + Conda

## 目录 / Table of Contents

1. [简介 / Introduction](#简介--introduction)  
2. [安装并配置 WSL2 (Ubuntu 22.04) / Installing & Configuring WSL2 (Ubuntu 22.04)](#安装并配置-wsl2-ubuntu-2204--installing--configuring-wsl2-ubuntu-2204)  
3. [启用 GPU 支持 / Enabling GPU Support](#启用-gpu-支持--enabling-gpu-support)  
4. [代理设置 / Proxy Configuration](#代理设置--proxy-configuration)  
   1. [WSL 全局代理 / System-wide Proxy in WSL](#wsl-全局代理--system-wide-proxy-in-wsl)  
   2. [Docker 代理 / Docker Proxy](#docker-代理--docker-proxy)  
     - [Docker `daemon.json` “default” 字段与其他写法 / About “default” vs “http-proxy” in `daemon.json`](#docker-daemonjson-default-字段与其他写法--about-default-vs-http-proxy-in-daemonjson)  
   3. [常见网络或 GPG Key 出错场景排查 / Common Network or GPG Key Errors](#常见网络或-gpg-key-出错场景排查--common-network-or-gpg-key-errors)  
5. [安装 Docker / Installing Docker](#安装-docker--installing-docker)  
   1. [官方仓库安装 / Official Repo Installation](#官方仓库安装--official-repo-installation)  
   2. [手动安装（离线或无法连接官方源） / Manual Installation (Offline or Repo Issues)](#手动安装离线或无法连接官方源--manual-installation-offline-or-repo-issues)  
6. [安装 Anaconda 并配置国内源 / Installing Anaconda & Configuring Mirrors](#安装-anaconda-并配置国内源--installing-anaconda--configuring-mirrors)  
   1. [Conda 国内源配置 / Conda Domestic Mirrors](#conda-国内源配置--conda-domestic-mirrors)  
   2. [Pip 国内源配置 / Pip Domestic Mirrors](#pip-国内源配置--pip-domestic-mirrors)  
   3. [Conda 与 Pip 源的区别 / Distinction between Conda and Pip Mirrors](#conda-与-pip-源的区别--distinction-between-conda-and-pip-mirrors)  
7. [创建大模型相关虚拟环境 / Creating LLM Virtual Environment](#创建大模型相关虚拟环境--creating-llm-virtual-environment)  
8. [可选：安装 CUDA & cuDNN / (Optional) Installing CUDA & cuDNN](#可选安装-cuda--cudnn--optional-installing-cuda--cudnn)  
9. [常见问题 / FAQ](#常见问题--faq)  
10. [总结 / Conclusion](#总结--conclusion)

---

## 简介 / Introduction

- **目标 / Goal**  
  1. 在 **Windows 11** 上通过 **WSL2 (Ubuntu 22.04)** 搭建一个可用的 GPU、Docker、代理、Conda 等大模型开发环境。  
  2. 使用宿主机（Windows）代理（如 Clash / V2Ray）在 WSL 中访问外网，包括 Docker 拉取镜像、Conda/Pip 安装包。  
  3. 避免常见 GPG Key、网络、仓库 404 等错误，并提供手动安装方式。  

- **范围 / Scope**  
  - 启用 GPU (NVIDIA) 支持  
  - 设置 WSL 系统级代理  
  - 设置 Docker 代理  
  - 安装 Docker（官方仓库 & 手动离线方式）  
  - 安装 Anaconda / Miniconda  
  - 配置国内镜像（Conda & Pip）  
  - （可选）安装 CUDA & cuDNN

---

## 安装并配置 WSL2 (Ubuntu 22.04) / Installing & Configuring WSL2 (Ubuntu 22.04)

1. **启用 WSL2 / Enable WSL2**  
   在 Windows PowerShell (管理员权限) 中执行：  
   ```powershell
   wsl --install
   ```
   安装完成后重启，再从 Microsoft Store 下载 **Ubuntu 22.04**。  

2. **基础更新 / Basic Update**  
   在 Ubuntu 中：  
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```
   配置好用户名、密码。

3. **(可选) 启用 systemd / Enable systemd (Optional)**  
   - 编辑 `/etc/wsl.conf`：
     ```ini
     [boot]
     systemd=true
     ```
   - 回到 Windows 命令行：
     ```powershell
     wsl --shutdown
     wsl
     ```
   - 现在 `systemctl` 可用了。

---

## 启用 GPU 支持 / Enabling GPU Support

1. **安装 NVIDIA 驱动 / Install NVIDIA Driver on Windows**  
   - 确保 Windows 上的 GPU 驱动与 CUDA for WSL2 兼容。  
2. **WSL 内验证 / Verify in WSL**  
   ```bash
   nvidia-smi
   ```
   能看到 GPU 信息表示支持正常。

---

## 代理设置 / Proxy Configuration

### 1. WSL 全局代理 / System-wide Proxy in WSL

**目的 / Goal**: 让 WSL 内所有程序（`apt-get`, `curl`, `conda`, etc.）通过宿主机代理访问外网。

1. **查找宿主机网关 IP / Find Host Gateway IP**  
   ```bash
   ip route | grep default
   ```
   输出如 `default via 172.17.176.1 dev eth0`，则 `172.17.176.1` 为宿主机 IP。

2. **设置环境变量 / Set Environment Variables**  
   编辑 `~/.bashrc` 或 `~/.zshrc`：
   ```bash
   export http_proxy="http://172.17.176.1:7890"
   export https_proxy="http://172.17.176.1:7890"
   export no_proxy="localhost,127.0.0.1"
   ```
   然后 `source ~/.bashrc`。

3. **测试 / Test**  
   ```bash
   curl -I https://www.google.com
   ```
   若返回 `HTTP/1.1 200 OK`，则代理可用。  

> **注意 / Note**: 需要宿主机代理工具（Clash / V2Ray 等）开启 **允许局域网访问**。

---

### 2. Docker 代理 / Docker Proxy

1. **编辑或创建 `/etc/docker/daemon.json`**  
   ```bash
   sudo nano /etc/docker/daemon.json
   ```
2. **写入以下配置 / Put the following content**  
   **注意**：有两种常见写法，**`"default": { ... }`** 或 **`"http-proxy": ...`**。  
   - 如果你的 Docker 版本支持 `"default"` 字段：
     ```json
     {
       "proxies": {
         "default": {
           "httpProxy": "http://172.17.176.1:7890",
           "httpsProxy": "http://172.17.176.1:7890",
           "noProxy": "localhost,127.0.0.1"
         }
       }
     }
     ```
   - 对于一些老版本 Docker 可能需要 `"http-proxy"` / `"https-proxy"` 而非 `"default"`：
     ```json
     {
       "proxies": {
         "http-proxy": "http://172.17.176.1:7890",
         "https-proxy": "http://172.17.176.1:7890",
         "no-proxy": "localhost,127.0.0.1"
       }
     }
     ```

3. **重启 Docker / Restart Docker**  
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart docker
   ```
   或者如果未启用 systemd：
   ```bash
   sudo service docker restart
   ```

4. **验证 / Verify**  
   ```bash
   docker info | grep -i proxy
   docker pull hello-world
   ```
   若成功拉取镜像，说明代理生效。

---

#### Docker `daemon.json` “default” 字段与其他写法 / About “default” vs “http-proxy” in `daemon.json`

- 新版本 Docker 通常支持：
  ```json
  "proxies": {
    "default": { ... }
  }
  ```
- 部分版本 Docker 仅支持：
  ```json
  "proxies": {
    "http-proxy": "http://...",
    "https-proxy": "http://...",
    "no-proxy": "..."
  }
  ```
- 如果看到 “the following directives are specified but not recognized” 或 “Failed to start Docker Application Container Engine” 日志，请切换另一种写法并重启 Docker。

---

### 3. 常见网络或 GPG Key 出错场景排查 / Common Network or GPG Key Errors

#### 3.1 “Could not handshake: Error in the pull function.”

- 可能网络或代理配置不对，导致无法访问 `https://download.docker.com`。
- 请先 `curl -I https://download.docker.com/linux/ubuntu/dists/jammy/InRelease` 测试是否可访问。

#### 3.2 “NO_PUBKEY 7EA0A9C3F273FCD8” / “GPG error: The repository is not signed.”

- Docker 官方 GPG Key 未正确导入或失效。
- 需要重新下载并 `sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg`。

#### 3.3 “Package docker-ce is not available” / “E: Unable to locate package docker-ce-cli”

- 可能是更新源失败、网络代理问题、或 Docker 源未添加成功。
- 手动查看 `/etc/apt/sources.list.d/docker.list` 是否正确，或者转为 **手动安装** Docker。

---

## 安装 Docker / Installing Docker

### 1. 官方仓库安装 / Official Repo Installation

**前提**：代理可用，Docker 源可正常访问。

1. **依赖 / Dependencies**  
   ```bash
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl gnupg lsb-release
   ```
2. **导入 GPG Key / GPG Key**  
   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
     | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   ```
3. **添加 Docker 源 / Repo**  
   ```bash
   echo \
   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
   https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
   | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```
4. **更新并安装 / Update & Install**  
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```
5. **验证 / Verify**  
   ```bash
   sudo systemctl start docker
   docker --version
   docker compose version
   ```

---

### 2. 手动安装（离线或无法连接官方源） / Manual Installation (Offline or Repo Issues)

1. **下载 `.deb` 包 / Download `.deb`**  
   从 [Docker Releases (Ubuntu)](https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/) 下载：
   - `docker-ce_<version>.deb`
   - `docker-ce-cli_<version>.deb`
   - `containerd.io_<version>.deb`
   - `docker-compose-plugin_<version>.deb` (可选)
2. **放进 WSL / Copy into WSL**  
   将下载好的文件放入 `/mnt/...` 或直接下载到 Linux 路径。
3. **安装 / Install**  
   ```bash
   sudo dpkg -i containerd.io_<version>.deb
   sudo dpkg -i docker-ce-cli_<version>.deb
   sudo dpkg -i docker-ce_<version>.deb
   sudo dpkg -i docker-compose-plugin_<version>.deb
   ```
4. **启动 & 测试 / Start & Test**  
   ```bash
   sudo service docker start
   docker pull hello-world
   ```

---

## 安装 Anaconda 并配置国内源 / Installing Anaconda & Configuring Mirrors

1. **下载并安装 Anaconda / Download & Install**  
   ```bash
   cd ~
   wget https://repo.anaconda.com/archive/Anaconda3-2023.07-2-Linux-x86_64.sh -O anaconda.sh
   chmod +x anaconda.sh
   ./anaconda.sh
   ```
   安装时选择 `yes` 初始化 `conda init`，或手动：
   ```bash
   conda init bash
   source ~/.bashrc
   ```

2. **验证 / Verify**  
   ```bash
   conda --version
   conda update --all
   ```

### 1. Conda 国内源配置 / Conda Domestic Mirrors

**切勿**将 `pypi/simple` 源错误地添加到 Conda channels，否则会报 404。

```bash
conda config --set show_channel_urls yes
# 以下示例以清华镜像为主, 其他如中科大/阿里可自行添加
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2
conda config --set channel_priority flexible
```

### 2. Pip 国内源配置 / Pip Domestic Mirrors

pip 的镜像源应写在 `~/.pip/pip.conf`：

```bash
mkdir -p ~/.pip
nano ~/.pip/pip.conf
```

示例（清华、阿里、USTC）：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
extra-index-url =
    https://mirrors.aliyun.com/pypi/simple
    https://pypi.mirrors.ustc.edu.cn/simple
[install]
trusted-host =
    pypi.tuna.tsinghua.edu.cn
    mirrors.aliyun.com
    pypi.mirrors.ustc.edu.cn
```

### 3. Conda 与 Pip 源的区别 / Distinction between Conda and Pip Mirrors

- **Conda Channels**：只适用于 `conda install`。
- **Pip Mirrors**：只适用于 `pip install`。
- 切勿将 `pypi/simple` 作为 conda channel，否则会报错。

---

## 创建大模型相关虚拟环境 / Creating LLM Virtual Environment

1. **创建并激活环境**  
   ```bash
   conda create -n llm python=3.12 -y
   conda activate llm
   ```
2. **安装常用库**  
   ```bash
   # 科学计算
   conda install scikit-learn -y
   # 大模型相关
   pip install transformers huggingface_hub modelscope langchain peft
   ```
3. **(可选) 安装 PyTorch GPU 等**  
   ```bash
   conda install pytorch torchvision torchaudio pytorch-cuda=12.2 -c pytorch -c nvidia
   ```

---

## 可选：安装 CUDA & cuDNN / (Optional) Installing CUDA & cuDNN

### 1. Conda 环境内安装 (推荐只做深度学习推理)

```bash
conda install -c nvidia cudatoolkit
conda install -c conda-forge cudnn
```

### 2. 系统级安装 (需要 `nvcc` 编译)

1. **在 Ubuntu (WSL) 中添加 CUDA 仓库并安装**  
2. **安装 cuDNN**（需登陆 NVIDIA 官网或下载 .deb 并解压到 `/usr/local`）。

---

## 常见问题 / FAQ

1. **WSL 无法访问外网**  
   - 检查代理是否允许 LAN 访问、WSL 中 IP 是否正确、环境变量是否设置正确。
2. **Docker 拉取镜像超时 / 失败**  
   - 检查 `/etc/docker/daemon.json` 中代理配置；重启 Docker 并查看 `docker info | grep -i proxy`。
3. **无法安装 Docker（NO_PUBKEY / 404）**  
   - 重新导入 GPG Key；或使用手动下载 `.deb` 包的安装方式。
4. **Conda 404 / pip 404**  
   - 确保不要把 `pypi` 镜像源当作 conda channel；Conda 与 Pip 源分别配置。
5. **默认 Docker `daemon.json` 中 “default” 字段无效**  
   - 改用 `"http-proxy"` / `"https-proxy"` 字段。  
6. **Systemd 未启动**  
   - 编辑 `/etc/wsl.conf` 开启 systemd 或手动用 `sudo service docker start` 启动 Docker。

---

## 总结 / Conclusion

通过以上步骤，你可以在 **Windows 11 + WSL2(Ubuntu 22.04)** 环境中：

1. **使用 GPU 进行加速**，例如深度学习推理或训练。  
2. **在 WSL 内使用宿主机代理**，包括 Docker 代理。  
3. **安装并运行 Docker**，解决网络或 GPG Key 问题。  
4. **安装 Anaconda/Miniconda** 并配置国内镜像，创建大模型相关虚拟环境。  
5. （可选）在系统级或 Conda 环境内安装 CUDA & cuDNN。

**祝使用顺利！**  
**Happy WSL2 + Docker + Conda + Proxy + GPU Development!**