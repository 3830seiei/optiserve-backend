# OptiServe 開発環境構築手順（WSL2 + Docker）

## 概要

このドキュメントは、Windows Server 2022 上の WSL2（Ubuntu 22.04）内で Docker コンテナを利用して FastAPI バックエンドを立ち上げ、**同一LAN上の別端末からAPI `/docs` にアクセス可能にするまでの構成・手順**を記録しています。

本構成は制限のある Windows 環境下での開発運用を目的としており、将来的には AWS 本番環境への移行を前提とします。

---

## システム構成

```plaintext
Windows Server 2022（192.168.99.118）
└─ WSL2 Ubuntu 22.04
   └─ Docker コンテナ
      └─ FastAPI (uvicorn)

````

---

## 1. 前提環境

- WSL2 + Ubuntu 22.04
- systemd 有効化済み
- Docker CE インストール済み
- `git` / `python3.12.9`（pyenv または base）導入済み

---

## 2. Docker デーモンの systemd 管理有効化

Docker が `systemctl` 管理下で起動できるよう、`override.conf` を追加：

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo vi /etc/systemd/system/docker.service.d/override.conf
````

内容：

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd
```

適用：

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl restart docker
```

確認：

```bash
sudo systemctl status docker
```

---

## 3. OptiServe リポジトリのクローン

```bash
cd ~/projects/
git clone git@github.com:3830seiei/smds_optiserve.git
cd smds_optiserve
git checkout feature/databasedesign
```

---

## 4. Dockerfile の準備（FastAPI 用）

プロジェクトルートに `Dockerfile` を作成：

```Dockerfile
FROM python:3.12.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## 5. Docker イメージビルドと起動

```bash
docker build -t optiserve .
docker run -d --name optiserve_dev -p 8000:8000 optiserve
```

※docker runコマンドはstart_docker.shで保存
※ログ/DB永続化は今後volume設定で追加予定。

---

## 6. Windows 側の portproxy 設定

WSL の Docker はそのままでは LAN からアクセス不可。
Windows の `netsh` で portproxy を追加：

```powershell
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=192.168.99.118 connectport=8000 connectaddress=172.31.56.43
```

※`connectaddress` には `ip addr` で確認した WSL の eth0 アドレスを指定。

確認：

```powershell
netsh interface portproxy show v4tov4
```

ポート8000をファイアウォールで開放する

```powershell
New-NetFirewallRule -DisplayName "Allow FastAPI 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

## 7. 外部端末からのアクセス確認

以下の URL にブラウザでアクセス：

```
http://192.168.99.118:8000/docs
```

✅ FastAPI の Swagger UI が表示されれば成功！

---

## 補足

### セキュリティ面について

* `docker.sock` を `tcp://0.0.0.0:2375` にしない（セキュリティリスク大）
* ポート開放時は Windows ファイアウォールも適切に制御
* 本構成は **開発用途限定**。本番運用では AWS EC2 + VPC を推奨

---

## 今後の予定

* MkDocs 用の別ポートによる公開
* Docker volume によるログ永続化
* PostgreSQL コンテナの追加（別ポート設定）
* FastAPI の本番起動（`--reload` なし）切り替え

