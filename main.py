import eel
import os
import time
import desktop
import method

# htmlファイルのディレクトリ
app_name="html"
# htmlファイル名
end_point="view.html"
# ウィンドウのサイズ
size=(550,550)

### 処理
@ eel.expose
def startYahuokuResearch(input_list):
    print("INFO：処理を開始します。")
    # インスタンス
    main = method.Main()

    # 入力パラメータチェック呼び出し、結果判定
    print("INFO：入力パラメータチェック開始")
    if not main.checkInputParameter(input_list):
        # Falseが返却された場合、エラーメッセージをアラートで表示
        eel.displayAlert(main.error_message)
        return
    print("INFO：入力パラメータチェック完了")
    
    # 商品タイトル一覧取得処理呼び出し(並行処理)
    print("INFO：商品タイトル一覧取得開始")
    main.parallelProcess("getProductTitleList", main.target_url_list)
    print("INFO：商品タイトル一覧取得完了")

    # 出品ページURL一覧取得処理呼び出し（並行処理）
    print("INFO：出品ページURL一覧取得開始")
    main.parallelProcess("getExhibitionPageUrlList", main.product_title_list)
    print("INFO：出品ページURL一覧取得完了")

    # 出品者情報一覧取得処理呼び出し（並行処理）
    print("INFO：出品者情報一覧取得開始")
    print("----------------------------------------")
    main.parallelProcess("getSellerInfoList", main.exhibition_page_url_list)
    print("INFO：出品者情報一覧取得完了")

    # CSVファイル出力処理呼び出し
    print("INFO：CSVファイル出力開始")
    main.outputCsv()
    print("INFO：CSVファイル出力完了")

    # 売上情報一覧取得処理呼び出し（並行処理）
    print("INFO：売上情報一覧取得開始")
    print("----------------------------------------")
    main.parallelProcess("getEarningsInfoList", main.yahoo_id_list)
    print("INFO：売上情報一覧取得完了")

    # CSVファイル更新処理呼び出し
    print("INFO：CSVファイル更新開始")
    main.updateCsv()
    print("INFO：CSVファイル更新完了")

    print("INFO：処理を終了します。")

    # 完了メッセージをアラート表示
    eel.displayAlert("処理が完了しました。 結果ファイル=" + main.result_csv)

# 画面生成処理呼び出し
desktop.start(app_name,end_point,size)