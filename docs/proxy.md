# 容器网络代理配置

## 环境信息

- **代理工具**: verge-mihomo
- **代理端口**: `7897`
- **代理地址**: `http://127.0.0.1:7897`
- **网络模式**: `host` (容器直接使用宿主机网络)

---

## 启用代理

在容器内执行以下命令设置代理:

```bash
# 设置 HTTP/HTTPS 代理
export http_proxy=http://127.0.0.1:7897
export https_proxy=http://127.0.0.1:7897
export HTTP_PROXY=http://127.0.0.1:7897
export HTTPS_PROXY=http://127.0.0.1:7897

# 设置 NO_PROXY (本地地址不走代理)
export NO_PROXY=localhost,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8
export no_proxy=localhost,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8
```

### 验证代理是否生效

```bash
# 查看代理环境变量
env | grep -i proxy

# 测试网络访问
curl -I https://www.google.com
```

---

## 关闭代理

在容器内执行以下命令取消代理:

```bash
# 取消所有代理环境变量
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
unset no_proxy NO_PROXY
```

---

## Git 代理配置

### 启用 Git 代理

```bash
git config --global http.proxy http://127.0.0.1:7897
git config --global https.proxy http://127.0.0.1:7897
```

### 关闭 Git 代理

```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 查看 Git 代理状态

```bash
git config --global --get http.proxy
git config --global --get https.proxy
```

---

## 常见问题

### apt-get 更新失败 (502 Bad Gateway)

verge-mihomo 代理可能对 `archive.ubuntu.com` 返回 502 错误。

**解决方案**: 临时取消代理后再执行 apt 操作:

```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
apt-get update && apt-get install -y <package-name>
```

### pip 安装失败

如果 pip 安装包超时或失败,可以尝试:

```bash
# 使用代理
pip install <package> --proxy http://127.0.0.1:7897

# 或不使用代理直接安装
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
pip install <package>
```

---

## 快捷命令

可以添加到 `~/.bashrc` 中的快捷函数:

```bash
# 开启代理
proxy_on() {
    export http_proxy=http://127.0.0.1:7897
    export https_proxy=http://127.0.0.1:7897
    export HTTP_PROXY=http://127.0.0.1:7897
    export HTTPS_PROXY=http://127.0.0.1:7897
    export NO_PROXY=localhost,127.0.0.1,::1
    export no_proxy=localhost,127.0.0.1,::1
    echo "代理已开启: http://127.0.0.1:7897"
}

# 关闭代理
proxy_off() {
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
    unset no_proxy NO_PROXY
    echo "代理已关闭"
}
```

使用方式:

```bash
source ~/.bashrc
proxy_on   # 开启代理
proxy_off  # 关闭代理
```
