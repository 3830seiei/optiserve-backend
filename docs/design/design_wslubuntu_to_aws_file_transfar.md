# オンプレミスからAWSへのファイルアップロード設計（アップロード方法 + セキュリティ対策 + コスト）

## 1. アップロード方法（S3利用）

- AWS S3 バケットを利用し、オンプレミス環境から直接アップロードする
- アップロード時は AWS CLI または AWS SDK を使用
- **署名付きURL**を発行し、そのURL宛にファイルをPUTする方式にすると、
  - 認証情報（アクセスキー）を直接オンプレ側に置かなくてよい
  - 有効期限付きの安全な一時アクセスが可能

**例：署名付きURL発行（有効期限1時間）**

```bash
aws s3 presign s3://my-bucket-name/myfile.csv --expires-in 3600
```

**例：署名付きURLでアップロード**

```bash
curl --upload-file ./myfile.csv "https://s3.amazonaws.com/my-bucket-name/myfile.csv?AWSAccessKeyId=...&Signature=...&Expires=..."
```

---

## 2. セキュリティ対策（三段構え）

### 2.1 通信経路の暗号化

- S3との通信はHTTPS（TLS1.2以上）で暗号化
- 署名付きURL利用により、直接的なアクセスキーの配布不要

### 2.2 保存時の暗号化（SSE-KMS）

- S3に保存されるデータをAWS Key Management Service (KMS) で暗号化
- **メリット**:
  - AWS管理のセキュリティ基準に沿った鍵管理
  - アクセス権限をIAMで細かく制御可能
  - アクセス履歴をCloudTrailに残せる

**アップロード時にSSE-KMSを指定**

```bash
aws s3 cp ./myfile.csv s3://my-bucket-name/ --sse aws:kms --sse-kms-key-id <KMS_KEY_ID>
```

### 2.3 ファイル自体の暗号化

- S3に送る前にファイル自体を暗号化（万一の流出対策）
- 推奨ツール：`age`（軽量で自動化向き）または `gpg`（企業利用での互換性高）
- 受信側は秘密鍵を用いて復号後に利用

**例：ageによる暗号化**

```bash
gzip -c myfile.csv > myfile.csv.gz
age -r <recipient-public-key> -o myfile.csv.gz.age myfile.csv.gz
```

---

## 3. コスト試算（SSE-KMS + ファイル暗号化 + 署名付きURL）

| 項目 | 単価（東京リージョン） | 備考 |
|------|------------------------|------|
| S3ストレージ | 約 $0.025／GB／月 | 例：200MBで約0.5円／月 |
| S3リクエスト | $0.005／1,000回 | 月1回なら無視できるレベル |
| データ転送 | 同リージョン内は無料 | インターネット経由ダウンロードは $0.114／GB |
| KMSキー管理 | 約 $1／月 | カスタマー管理キー（CMK）1本あたり |
| KMSリクエスト | $0.03／1,000回 | 月1回アップ+ダウンなら0円に近い |
| ファイル暗号化 | 0円 | ローカル処理（age/gpg） |

**月1回200MBファイルの場合の概算**

- ストレージ：約0.5円
- KMSキー管理：約150円
- リクエスト・転送：ほぼ0円（同リージョン）
- **合計：約150〜160円／月**

---

## 4. 運用上のポイント

- **鍵管理**: 暗号化に使う公開鍵は送信側、秘密鍵は受信側で安全に保管
- **IAMポリシーの最小権限化**: アップロード専用ユーザー／ロールを作成
- **監査ログ**: CloudTrailでKMS利用・S3アクセスの記録を取得
- **定期ローテーション**: KMSキー・暗号鍵は定期的に更新

---

## 5. 【補足】S3へのファイル配置をイベントとした仕組み

### アーキテクチャ（軽量・堅牢）

S3 (ObjectCreated, prefix/suffixで絞る)
→ EventBridge（配線）
→ SQS（キュー/再試行/順序担保）
→ オンプレPythonワーカー（長ポーリングで受信 → S3から取得 → 検証/復号/取込）

重処理はオンプレ側で実行。Lambdaは使わずに済むので、サイズ制限やタイムアウトを気にしなくてOK。
SQSは長ポーリングでリクエスト数が少なく、コストもごく小さいです。

### 具体ステップ（要点だけ）

1) S3イベント設定
    - 対象バケットにEventBridge通知を有効化
    - prefix: incoming/（フォルダ代わり）
    - suffix: .csv.gz.age（暗号化済みCSVの例）
    - ついでにSSE-KMSをデフォルト有効化（バケット暗号化）

2) EventBridge → SQS ルール
    - ルールで detail.object.key が incoming/ かつ *.csv.gz.age にマッチするイベントだけ送る
    - SQSキューは
    - 可視性タイムアウト：処理時間+余裕
    - DLQ（デッドレターキュー）を関連付け
    - 暗号化（SSE-SQS or KMS）有効

3) IAM最小権限
    - オンプレワーカー用IAMユーザー/ロール（アクセスキーを保管）
    - sqs:ReceiveMessage, DeleteMessage, ChangeMessageVisibility（対象キューのみ）
    - s3:GetObject, GetObjectTagging, HeadObject（対象バケット + prefix のみ）
    - KMS復号が必要なら kms:Decrypt（対象キーのみ）

4) オンプレPythonワーカー（長ポーリング）
    - SQSを**長ポーリング（WaitTimeSeconds=20）**で受信
    - メッセージから bucket/key を取得
    - S3からファイルGET → ハッシュ/署名検証 → 復号（age/gpg） → \copyでステージング → Upsert
    - 冪等性：key + ETag or VersionId で「既処理」テーブル/ファイルに記録
    - 正常完了で DeleteMessage、失敗は例外投げてSQSの再試行に任せる

```Python
import json, time, urllib.parse, boto3, botocore

sqs = boto3.client("sqs")
s3  = boto3.client("s3")

QUEUE_URL = "https://sqs.ap-northeast-1.amazonaws.com/123456789012/my-incoming-queue"

def receive_loop():
    while True:
        resp = sqs.receive_message(
            QueueUrl=QUEUE_URL, MaxNumberOfMessages=5,
            WaitTimeSeconds=20, VisibilityTimeout=180
        )
        for m in resp.get("Messages", []):
            try:
                evt = json.loads(m["Body"])
                rec = json.loads(evt["Records"][0]["body"]) if "Records" in evt else evt
                # EventBridge→SQS経由の場合のpayload整形は環境で要確認
                bucket = rec["detail"]["bucket"]["name"]
                key = urllib.parse.unquote(rec["detail"]["object"]["key"])

                if not key.startswith("incoming/") or not key.endswith(".csv.gz.age"):
                    sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=m["ReceiptHandle"])
                    continue

                # 1) S3ダウンロード
                tmp = f"/tmp/{key.split('/')[-1]}"
                s3.download_file(bucket, key, tmp)

                # 2) 署名/ハッシュ検証 → 復号（age/gpgをサブプロセス実行）
                # 3) gunzip → CSVを\copyで取り込み → Upsert & watermark更新

                # 4) 完了
                sqs.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=m["ReceiptHandle"])

            except Exception as e:
                # 失敗→可視性タイムアウト後に再配信、一定回数でDLQへ
                print("error:", e)

        time.sleep(1)

if __name__ == "__main__":
    receive_loop()
```

受け取るイベントのJSON形は配線方法で少し違うので、最初に print(m["Body"]) で実物を確認してパースを微調整してください。

### コスト感（概算）

- S3イベント通知/ EventBridge ルール：ほぼ無料（イベント数依存だが月1〜数回なら無視）
- SQS：リクエスト課金だが長ポーリングで低頻度 → 月数円〜数十円レベル
- オンプレ側：常駐プロセスのCPU/ネットワークのみ
- KMS/S3：前に計算した通り、月150円前後（キー管理）＋保管料ほぼゼロ

### 運用Tips

- prefix & suffixで対象を厳密に絞る（誤通知防止）
- DLQを必ず有効化（解析しやすい）
- 冪等（同じオブジェクト重複通知でも二重取り込みしない）
- 大サイズは分割 or マニフェスト採用（1件巨大より複数小分けが安定）
- テストは別の incoming/test/ プレフィックスを使い、本番と同じ経路で通す

