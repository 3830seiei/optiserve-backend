"""test_file_management_api.py

pytestを使用してファイル管理APIのテストを行います。

実行方法
- startup_optiserve.shを実行してAPIサーバーを起動
- pytest tests/test_file_management_api.py -v

前提条件:
- medical_id=6でテスト用医療機関が登録済みであること
- テスト実行前に自動でクリーンアップが実行されます
- ファイルアップロード・ダウンロード機能の統合テスト
"""

import pytest
import requests
import random
import string
import json
import sys
import os
import tempfile
from pathlib import Path
import io

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# OS環境に応じた動的パス設定をテストでも使用
try:
    from src.utils.path_config import path_config
    USE_DYNAMIC_PATHS = True
except ImportError:
    USE_DYNAMIC_PATHS = False

# 環境に応じたAPI接続先の自動判定
API_HOST = os.environ.get("OPTISERVE_API_HOST", "localhost")
BASE_URL = f"http://{API_HOST}:8000/api/v1"

# テスト用の共通ヘッダー（認証情報）
TEST_HEADERS = {"X-User-Id": "900001"}  # システム管理者のuser_id

def cleanup_test_files():
    """テスト実行前のクリーンアップ - テスト用ファイルとDBレコードを削除"""
    try:
        print("🔍 クリーンアップ開始: テストファイルとDBレコードをチェック中...")
        
        # テスト用ファイルディレクトリの削除（年/月階層構造対応）
        if USE_DYNAMIC_PATHS:
            test_file_dirs = [
                path_config.uploads_path / "6",  # テスト用医療機関ID=6
                path_config.uploads_path / "999",  # 存在しない医療機関ID用
                path_config.reports_path / "6",  # 医療機関ID=6の年/月フォルダを全削除
                path_config.reports_path / "5",  # 医療機関ID=5の年/月フォルダを全削除（オンプレミスレポートテスト用）
            ]
        else:
            # フォールバック: 従来のハードコードパス
            test_file_dirs = [
                Path("files/uploads/6"),  # テスト用医療機関ID=6
                Path("files/uploads/999"),  # 存在しない医療機関ID用
                Path("files/reports/6"),  # 医療機関ID=6の年/月フォルダを全削除
                Path("files/reports/5"),  # 医療機関ID=5の年/月フォルダを全削除（オンプレミスレポートテスト用）
            ]
        
        cleaned_dirs = 0
        for test_dir in test_file_dirs:
            if test_dir.exists():
                import shutil
                shutil.rmtree(test_dir)
                cleaned_dirs += 1
                print(f"削除済みディレクトリ: {test_dir}")
        
        # DB履歴のクリーンアップ（直接DB操作）
        try:
            from src.database import SessionLocal
            from src.models.pg_optigate.facility_upload_log import FacilityUploadLog
            from src.models.pg_optigate.report_publication_log import ReportPublicationLog
            
            db = SessionLocal()
            try:
                # テスト用医療機関のアップロードログを削除
                deleted_upload_logs = db.query(FacilityUploadLog).filter(
                    FacilityUploadLog.medical_id.in_([6, 999])
                ).delete(synchronize_session=False)
                
                # テスト用医療機関のレポート公開ログを削除
                deleted_report_logs = db.query(ReportPublicationLog).filter(
                    ReportPublicationLog.medical_id.in_([5, 6, 999])
                ).delete(synchronize_session=False)
                
                db.commit()
                print(f"🧹 DB クリーンアップ: アップロードログ{deleted_upload_logs}件, レポートログ{deleted_report_logs}件を削除")
                
            except Exception as e:
                print(f"DB クリーンアップエラー: {e}")
                db.rollback()
            finally:
                db.close()
                
        except ImportError as e:
            print(f"DB モジュールインポートエラー (テスト続行): {e}")
        
        if cleaned_dirs > 0:
            print(f"✨ ファイルクリーンアップ完了: {cleaned_dirs}個のディレクトリを削除")
        else:
            print("✨ クリーンアップ対象なし: テストファイルは存在しません")
            
    except Exception as e:
        print(f"クリーンアップ処理でエラーが発生しましたが、テストを続行します: {e}")
        import traceback
        print(f"詳細エラー: {traceback.format_exc()}")

@pytest.fixture(scope="session", autouse=False)
def setup_test_environment():
    """テスト環境のセットアップ - 手動実行時のみクリーンアップ"""
    print("\\n🚀 ファイル管理テスト環境セットアップ開始...")
    cleanup_test_files()
    print("✅ ファイル管理テスト環境セットアップ完了\\n")

def random_string(length=6):
    """ランダムな文字列生成"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_test_csv_file(filename: str = "test.csv", content: str = None) -> io.BytesIO:
    """テスト用CSVファイル作成"""
    if content is None:
        content = f"id,name,date\\n1,テスト機器_{random_string()},2025-01-01\\n2,テスト機器2,2025-01-02\\n"
    
    file_obj = io.BytesIO(content.encode('utf-8'))
    file_obj.name = filename
    return file_obj

def test_api_server_is_running():
    """APIサーバーが起動していることを確認"""
    try:
        res = requests.get(f"{BASE_URL}/user-entity-links/", timeout=5, headers=TEST_HEADERS)
        assert res.status_code in [200, 404], f"APIサーバーが応答しません: status_code={res.status_code}"
        print("✅ APIサーバー稼働確認完了")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"APIサーバーに接続できません。startup_optiserve.shでサーバーを起動してください: {e}")

def test_file_upload_success():
    """ファイルアップロード成功テスト"""
    medical_id = 6
    upload_user_id = "1"
    
    # テスト用CSVファイルを作成
    equipment_file = create_test_csv_file("equipment.csv", "機器ID,機器名,設置日\\n1,MRI,2024-01-01\\n")
    rental_file = create_test_csv_file("rental.csv", "貸出ID,機器ID,貸出日\\n1,1,2024-12-01\\n")
    failure_file = create_test_csv_file("failure.csv", "故障ID,機器ID,故障日\\n1,1,2024-11-15\\n")
    
    files = {
        'equipment_file': ('equipment.csv', equipment_file, 'text/csv'),
        'rental_file': ('rental.csv', rental_file, 'text/csv'), 
        'failure_file': ('failure.csv', failure_file, 'text/csv')
    }
    
    data = {
        'upload_user_id': upload_user_id
    }
    
    res = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}", 
        files=files,
        data=data,
        headers=TEST_HEADERS
    )
    
    print(f"レスポンス: status_code={res.status_code}")
    if res.status_code != 200:
        print(f"エラー詳細: {res.text}")
    
    assert res.status_code == 200
    response_data = res.json()
    
    # レスポンス検証
    assert response_data["medical_id"] == medical_id
    assert "target_month" in response_data  # 実行月が記録される
    assert "upload_datetime" in response_data
    assert len(response_data["uploaded_files"]) == 3
    assert response_data["notification_sent"] in [True, False]  # 通知機能は実装状況による
    
    # アップロードされたファイルの検証
    for uploaded_file in response_data["uploaded_files"]:
        assert uploaded_file["medical_id"] == medical_id
        assert uploaded_file["file_type"] in [1, 2, 3]
        assert uploaded_file["upload_user_id"] == upload_user_id
    
    print(f"✅ ファイルアップロード成功: medical_id={medical_id}, 実行月={response_data['target_month']}")
    print(f"   アップロードファイル数: {len(response_data['uploaded_files'])}件")

def test_file_upload_nonexistent_medical_id():
    """存在しない医療機関IDでのアップロードエラーテスト"""
    medical_id = 99999  # 存在しない医療機関ID
    upload_user_id = "1"
    
    equipment_file = create_test_csv_file("equipment.csv")
    rental_file = create_test_csv_file("rental.csv") 
    failure_file = create_test_csv_file("failure.csv")
    
    files = {
        'equipment_file': ('equipment.csv', equipment_file, 'text/csv'),
        'rental_file': ('rental.csv', rental_file, 'text/csv'),
        'failure_file': ('failure.csv', failure_file, 'text/csv')
    }
    
    data = {
        'upload_user_id': upload_user_id
    }
    
    res = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}",
        files=files,
        data=data,
        headers=TEST_HEADERS
    )
    
    assert res.status_code == 400
    error = res.json()
    assert "は存在しません" in error["detail"]
    print(f"✅ 存在しない医療機関IDエラー: {error['detail']}")

def test_file_upload_wrong_file_extension():
    """間違ったファイル拡張子でのアップロードエラーテスト"""
    medical_id = 6
    upload_user_id = "1"
    
    # テキストファイルをCSVとして送信（エラーになるべき）
    equipment_file = io.BytesIO(b"This is not a CSV file")
    equipment_file.name = "equipment.txt"  # .txt拡張子
    
    rental_file = create_test_csv_file("rental.csv")
    failure_file = create_test_csv_file("failure.csv")
    
    files = {
        'equipment_file': ('equipment.txt', equipment_file, 'text/plain'),
        'rental_file': ('rental.csv', rental_file, 'text/csv'),
        'failure_file': ('failure.csv', failure_file, 'text/csv')
    }
    
    data = {
        'upload_user_id': upload_user_id
    }
    
    res = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}",
        files=files,
        data=data,
        headers=TEST_HEADERS
    )
    
    assert res.status_code == 400
    error = res.json()
    assert "CSV形式" in error["detail"]
    print(f"✅ 無効なファイル拡張子エラー: {error['detail']}")

def test_file_upload_missing_file():
    """ファイル不足でのアップロードエラーテスト"""
    medical_id = 6
    upload_user_id = "1"
    
    # 1つのファイルのみ送信（3つ必要なのに不足）
    equipment_file = create_test_csv_file("equipment.csv")
    
    files = {
        'equipment_file': ('equipment.csv', equipment_file, 'text/csv'),
        # rental_file と failure_file が不足
    }
    
    data = {
        'upload_user_id': upload_user_id
    }
    
    res = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}",
        files=files,
        data=data,
        headers=TEST_HEADERS
    )
    
    assert res.status_code == 422  # FastAPIのバリデーションエラー
    print("✅ ファイル不足エラー確認完了")

def test_file_upload_overwrite():
    """ファイル上書きテスト"""
    medical_id = 6
    upload_user_id = "1"
    
    # 1回目のアップロード
    equipment_file1 = create_test_csv_file("equipment_v1.csv", "ID,名前\\n1,初回機器\\n")
    rental_file1 = create_test_csv_file("rental_v1.csv")
    failure_file1 = create_test_csv_file("failure_v1.csv")
    
    files1 = {
        'equipment_file': ('equipment_v1.csv', equipment_file1, 'text/csv'),
        'rental_file': ('rental_v1.csv', rental_file1, 'text/csv'),
        'failure_file': ('failure_v1.csv', failure_file1, 'text/csv')
    }
    
    data1 = {
        'upload_user_id': upload_user_id
    }
    
    res1 = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}",
        files=files1,
        data=data1,
        headers=TEST_HEADERS
    )
    
    assert res1.status_code == 200
    response1 = res1.json()
    print(f"✅ 1回目アップロード成功: {len(response1['uploaded_files'])}件")
    
    # 2回目のアップロード（上書き）
    equipment_file2 = create_test_csv_file("equipment_v2.csv", "ID,名前\\n1,更新済み機器\\n")
    rental_file2 = create_test_csv_file("rental_v2.csv")
    failure_file2 = create_test_csv_file("failure_v2.csv")
    
    files2 = {
        'equipment_file': ('equipment_v2.csv', equipment_file2, 'text/csv'),
        'rental_file': ('rental_v2.csv', rental_file2, 'text/csv'),
        'failure_file': ('failure_v2.csv', failure_file2, 'text/csv')
    }
    
    data2 = {
        'upload_user_id': upload_user_id
    }
    
    res2 = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}",
        files=files2,
        data=data2,
        headers=TEST_HEADERS
    )
    
    assert res2.status_code == 200
    response2 = res2.json()
    
    # 2回目の方が新しい時刻であることを確認
    assert response2["upload_datetime"] > response1["upload_datetime"]
    print(f"✅ 上書きアップロード成功: 1回目={response1['upload_datetime'][:19]}, 2回目={response2['upload_datetime'][:19]}")

def test_upload_status_endpoint():
    """アップロード状況確認エンドポイントテスト"""
    medical_id = 6
    
    res = requests.get(f"{BASE_URL}/files/upload-status/{medical_id}", headers=TEST_HEADERS)
    
    # 現在は空の配列を返す実装（TODO実装済みの場合は変更）
    if res.status_code == 200:
        status_list = res.json()
        assert isinstance(status_list, list)
        print(f"✅ アップロード状況取得成功: {len(status_list)}件の状況データ")
    else:
        # 501 Not Implemented の場合も正常（未実装のため）
        assert res.status_code in [200, 501]
        print("✅ アップロード状況エンドポイント確認完了（未実装または実装済み）")

def test_available_reports_endpoint():
    """利用可能レポート一覧エンドポイントテスト"""
    medical_id = 6
    
    res = requests.get(f"{BASE_URL}/files/reports/available/{medical_id}", headers=TEST_HEADERS)
    
    # 現在は空の配列を返す実装（TODO実装済みの場合は変更）
    if res.status_code == 200:
        reports_list = res.json()
        assert isinstance(reports_list, list)
        print(f"✅ 利用可能レポート取得成功: {len(reports_list)}件のレポート")
    else:
        # 501 Not Implemented の場合も正常（未実装のため）
        assert res.status_code in [200, 501]
        print("✅ 利用可能レポートエンドポイント確認完了（未実装または実装済み）")

def test_system_file_download_success():
    """システム用ファイルダウンロード成功テスト"""
    medical_id = 6
    system_key = "optiserve-internal-system-key-2025"
    
    # まずファイルをアップロードしてダウンロード対象を準備
    upload_user_id = "1"
    
    equipment_file = create_test_csv_file("test_equipment.csv", "ID,名前,型番\n1,機器A,MODEL-001\n2,機器B,MODEL-002\n")
    rental_file = create_test_csv_file("test_rental.csv", "日付,機器ID,貸出先\n2025-01-01,1,部署A\n")
    failure_file = create_test_csv_file("test_failure.csv", "日付,機器ID,故障内容\n2025-01-05,1,電源不良\n")
    
    files = {
        'equipment_file': ('test_equipment.csv', equipment_file, 'text/csv'),
        'rental_file': ('test_rental.csv', rental_file, 'text/csv'),
        'failure_file': ('test_failure.csv', failure_file, 'text/csv')
    }
    
    data = {
        'upload_user_id': upload_user_id
    }
    
    # アップロード実行
    upload_res = requests.post(
        f"{BASE_URL}/files/upload-files/{medical_id}",
        files=files,
        data=data,
        headers=TEST_HEADERS
    )
    assert upload_res.status_code == 200
    print("✅ テスト用ファイルアップロード完了")
    
    # 各ファイル種別のダウンロードテスト
    for file_type in [1, 2, 3]:
        headers = {"X-System-Key": system_key}
        download_res = requests.get(
            f"{BASE_URL}/files/system/fetch-uploaded/{medical_id}",
            params={"file_type": file_type},
            headers=headers
        )
        
        assert download_res.status_code == 200
        assert download_res.headers.get('content-type') == 'text/csv; charset=utf-8'
        
        # ファイル内容確認
        content = download_res.text
        assert len(content) > 0
        assert "," in content  # CSVの基本フォーマット確認
        
        file_names = {1: "equipment.csv", 2: "rental.csv", 3: "failure.csv"}
        print(f"✅ システムファイルダウンロード成功: {file_names[file_type]} (ファイル種別={file_type})")

def test_system_file_download_unauthorized():
    """システム用ファイルダウンロード認証エラーテスト"""
    medical_id = 6
    file_type = 1
    
    # APIキーなしでアクセス
    download_res = requests.get(
        f"{BASE_URL}/files/system/fetch-uploaded/{medical_id}",
        params={"file_type": file_type}
    )
    assert download_res.status_code == 401
    print("✅ 認証エラーテスト成功: APIキーなしで401エラー")
    
    # 間違ったAPIキーでアクセス
    headers = {"X-System-Key": "wrong-key"}
    download_res2 = requests.get(
        f"{BASE_URL}/files/system/fetch-uploaded/{medical_id}",
        params={"file_type": file_type},
        headers=headers
    )
    assert download_res2.status_code == 401
    print("✅ 認証エラーテスト成功: 間違ったAPIキーで401エラー")

def test_system_file_download_file_not_found():
    """システム用ファイルダウンロード ファイル未存在テスト"""
    medical_id = 999  # 存在しない医療機関ID
    file_type = 1
    system_key = "optiserve-internal-system-key-2025"
    
    headers = {"X-System-Key": system_key}
    download_res = requests.get(
        f"{BASE_URL}/files/system/fetch-uploaded/{medical_id}",
        params={"file_type": file_type},
        headers=headers
    )
    
    assert download_res.status_code == 404
    print("✅ ファイル未存在テスト成功: 存在しない医療機関IDで404エラー")

def test_system_file_download_invalid_file_type():
    """システム用ファイルダウンロード 無効なファイル種別テスト"""
    medical_id = 6
    invalid_file_type = 99
    system_key = "optiserve-internal-system-key-2025"
    
    headers = {"X-System-Key": system_key}
    download_res = requests.get(
        f"{BASE_URL}/files/system/fetch-uploaded/{medical_id}",
        params={"file_type": invalid_file_type},
        headers=headers
    )
    
    assert download_res.status_code == 400
    print("✅ 無効なファイル種別テスト成功: ファイル種別99で400エラー")

def test_publish_reports_unauthorized():
    """レポート公開エンドポイント認証エラーテスト"""
    medical_id = 6
    publication_ym = "2025-01"
    
    data = {
        'publication_ym': publication_ym
    }
    
    # APIキーなしでアクセス
    publish_res = requests.post(
        f"{BASE_URL}/files/reports/publish/{medical_id}",
        data=data
    )
    assert publish_res.status_code == 401
    print("✅ レポート公開認証エラーテスト成功: APIキーなしで401エラー")
    
    # 間違ったAPIキーでアクセス
    headers = {"X-System-Key": "wrong-key"}
    publish_res2 = requests.post(
        f"{BASE_URL}/files/reports/publish/{medical_id}",
        data=data,
        headers=headers
    )
    assert publish_res2.status_code == 401
    print("✅ レポート公開認証エラーテスト成功: 間違ったAPIキーで401エラー")

def test_publish_reports_with_auth():
    """レポート公開エンドポイント認証成功テスト（オンプレミスレポートが存在しない場合の404エラー期待）"""
    medical_id = 6
    publication_ym = "2025-01"
    system_key = "optiserve-internal-system-key-2025"
    
    data = {
        'publication_ym': publication_ym
    }
    headers = {"X-System-Key": system_key}
    
    publish_res = requests.post(
        f"{BASE_URL}/files/reports/publish/{medical_id}",
        data=data,
        headers=headers
    )
    
    # 認証は通過するが、オンプレミスレポートが存在しないため404エラーが期待値
    assert publish_res.status_code == 404
    assert "オンプレミスレポートが見つかりません" in publish_res.json().get("detail", "")
    print("✅ レポート公開認証成功テスト完了: 認証通過後に404エラー（オンプレミスレポート未存在）")

def test_publish_onpremise_reports():
    """オンプレミスレポート公開テスト（hpcode=5、2025-05月分）"""
    medical_id = 5
    publication_ym = "2025-05"
    system_key = "optiserve-internal-system-key-2025"
    
    data = {
        'publication_ym': publication_ym
    }
    headers = {"X-System-Key": system_key}
    
    publish_res = requests.post(
        f"{BASE_URL}/files/reports/publish/{medical_id}",
        data=data,
        headers=headers
    )
    
    if publish_res.status_code != 200:
        print(f"❌ エラー詳細: {publish_res.status_code}, {publish_res.text}")
    assert publish_res.status_code == 200
    response_data = publish_res.json()
    
    # レスポンス内容確認
    assert response_data["medical_id"] == medical_id
    assert response_data["publication_ym"] == publication_ym
    assert "publish_datetime" in response_data
    assert "published_reports" in response_data
    assert len(response_data["published_reports"]) > 0
    
    # ファイル情報確認
    published_file = response_data["published_reports"][0]
    assert published_file["file_name"] == "hpreport-05_20250804.pptx"
    assert published_file["file_type"] == 1  # PPTXファイルなので分析レポートとして分類
    
    print(f"✅ オンプレミスレポート公開成功: {len(response_data['published_reports'])}件のファイルを公開")
    print(f"   公開ファイル: {published_file['file_name']} (ID: {published_file['publication_id']})")
    
    # ファイルが実際にコピーされたか確認（年/月階層構造、月は0埋め2桁）
    import os
    year, month = publication_ym.split("-")
    month_int = int(month)
    month_padded = f"{month_int:02d}"  # 月を0埋め2桁に
    if USE_DYNAMIC_PATHS:
        copied_file_path = path_config.reports_path / str(medical_id) / year / month_padded / "hpreport-05_20250804.pptx"
    else:
        copied_file_path = f"files/reports/{medical_id}/{year}/{month_padded}/hpreport-05_20250804.pptx"
    assert os.path.exists(copied_file_path), f"コピーされたファイルが見つかりません: {copied_file_path}"
    print(f"✅ ファイルコピー確認完了: {copied_file_path}")

def test_publish_nonexistent_onpremise_reports():
    """存在しないオンプレミスレポート公開エラーテスト"""
    medical_id = 999  # 存在しない医療機関ID
    publication_ym = "2025-12"  # 存在しない年月
    system_key = "optiserve-internal-system-key-2025"
    
    data = {
        'publication_ym': publication_ym
    }
    headers = {"X-System-Key": system_key}
    
    publish_res = requests.post(
        f"{BASE_URL}/files/reports/publish/{medical_id}",
        data=data,
        headers=headers
    )
    
    assert publish_res.status_code == 404
    assert "医療機関ID" in publish_res.json().get("detail", "")
    print("✅ 存在しない医療機関IDでレポート公開エラーテスト成功")

def test_report_download_after_publish():
    """レポート公開後のダウンロードテスト（user_id=10）"""
    medical_id = 5
    publication_ym = "2025-05"
    system_key = "optiserve-internal-system-key-2025"
    download_user_id = "10"
    
    # Step 1: レポートを公開（まず公開されたレポートのpublication_idを取得）
    data = {
        'publication_ym': publication_ym
    }
    headers = {"X-System-Key": system_key}
    
    publish_res = requests.post(
        f"{BASE_URL}/files/reports/publish/{medical_id}",
        data=data,
        headers=headers
    )
    
    if publish_res.status_code != 200:
        # 既に公開済みの場合は問題なし
        print(f"⚠️ レポート公開結果: {publish_res.status_code} (既に公開済みの可能性)")
    else:
        publish_data = publish_res.json()
        print(f"✅ レポート公開成功: {len(publish_data['published_reports'])}件")
    
    # Step 2: DBから最新のpublication_idを取得してダウンロード実行
    from src.database import SessionLocal
    from src.models.pg_optigate.report_publication_log import ReportPublicationLog
    
    db = SessionLocal()
    try:
        # 対象医療機関・年月の最新レポートを取得
        latest_report = db.query(ReportPublicationLog).filter(
            ReportPublicationLog.medical_id == medical_id,
            ReportPublicationLog.publication_ym == publication_ym
        ).order_by(ReportPublicationLog.upload_datetime.desc()).first()
        
        if not latest_report:
            raise Exception(f"公開されたレポートが見つかりません: 医療機関ID={medical_id}, 年月={publication_ym}")
        
        publication_id = latest_report.publication_id
        print(f"📋 取得したpublication_id: {publication_id}")
        
        # ダウンロード前のDB状態を記録
        download_datetime_before = latest_report.download_datetime
        download_user_id_before = latest_report.download_user_id
        print(f"📊 ダウンロード前状態: download_user_id={download_user_id_before}, download_datetime={download_datetime_before}")
        
    finally:
        db.close()
    
    # Step 3: レポートダウンロード実行
    download_res = requests.get(
        f"{BASE_URL}/files/reports/download/{publication_id}",
        params={"user_id": download_user_id},
        headers=TEST_HEADERS
    )
    
    assert download_res.status_code == 200
    assert download_res.headers.get('content-type') == 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    
    # ファイル内容の基本チェック
    content = download_res.content
    assert len(content) > 1000000  # PPTXファイルなので1MB以上はあるはず
    print(f"✅ レポートダウンロード成功: ファイルサイズ {len(content)} bytes")
    
    # Step 4: DB更新状況の確認
    db = SessionLocal()
    try:
        updated_report = db.query(ReportPublicationLog).filter(
            ReportPublicationLog.publication_id == publication_id
        ).first()
        
        # DB更新の確認
        assert updated_report.download_user_id == download_user_id, f"download_user_idが更新されていません: 期待値={download_user_id}, 実際値={updated_report.download_user_id}"
        assert updated_report.download_datetime is not None, "download_datetimeが更新されていません"
        
        # 初回ダウンロードの場合のみ更新されることの確認
        if download_datetime_before is None:
            print(f"✅ 初回ダウンロード記録更新: user_id={updated_report.download_user_id}, datetime={updated_report.download_datetime}")
        else:
            print(f"✅ 既存ダウンロード記録維持: user_id={updated_report.download_user_id}, datetime={updated_report.download_datetime}")
            
    finally:
        db.close()

def test_report_download_nonexistent_publication():
    """存在しないpublication_idでのダウンロードエラーテスト"""
    nonexistent_publication_id = 99999
    user_id = "10"
    
    download_res = requests.get(
        f"{BASE_URL}/files/reports/download/{nonexistent_publication_id}",
        params={"user_id": user_id},
        headers=TEST_HEADERS
    )
    
    assert download_res.status_code == 404
    assert "存在しません" in download_res.json().get("detail", "")
    print("✅ 存在しないpublication_IDでダウンロードエラーテスト成功")

def test_report_download_multiple_times():
    """同一レポートの複数回ダウンロードテスト（DB更新は初回のみ）"""
    medical_id = 5
    publication_ym = "2025-05"
    user_id_1 = "10"
    user_id_2 = "1"  # 異なるユーザー
    
    # 最新レポートのpublication_idを取得
    from src.database import SessionLocal
    from src.models.pg_optigate.report_publication_log import ReportPublicationLog
    
    db = SessionLocal()
    try:
        latest_report = db.query(ReportPublicationLog).filter(
            ReportPublicationLog.medical_id == medical_id,
            ReportPublicationLog.publication_ym == publication_ym
        ).order_by(ReportPublicationLog.upload_datetime.desc()).first()
        
        if not latest_report:
            print("⚠️ テスト用レポートが見つかりません。先にtest_report_download_after_publishを実行してください")
            return
            
        publication_id = latest_report.publication_id
        
        # 1回目のダウンロード（既に実行済みの想定）
        first_download_user_id = latest_report.download_user_id
        first_download_datetime = latest_report.download_datetime
        
    finally:
        db.close()
    
    # 2回目のダウンロード（別ユーザー）
    download_res = requests.get(
        f"{BASE_URL}/files/reports/download/{publication_id}",
        params={"user_id": user_id_2},
        headers=TEST_HEADERS
    )
    
    assert download_res.status_code == 200
    print(f"✅ 2回目ダウンロード成功: user_id={user_id_2}")
    
    # DB状態確認（初回ダウンロード情報が保持されることの確認）
    db = SessionLocal()
    try:
        report_after_second_download = db.query(ReportPublicationLog).filter(
            ReportPublicationLog.publication_id == publication_id
        ).first()
        
        # 初回ダウンロード情報が保持されていることを確認
        assert report_after_second_download.download_user_id == first_download_user_id, "初回ダウンロードユーザーIDが変更されています"
        assert report_after_second_download.download_datetime == first_download_datetime, "初回ダウンロード日時が変更されています"
        
        print(f"✅ DB状態確認: 初回ダウンロード情報が保持されています (user_id={first_download_user_id})")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("ファイル管理APIテストを実行します...")
    print("前提: APIサーバーがlocalhost:8000で起動していること")
    print("前提: medical_id=6でテスト用医療機関が登録済みであること")