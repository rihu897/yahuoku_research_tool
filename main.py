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
    print("処理を開始します。")
    # インスタンス
    main = method.Main()

    # 入力パラメータチェック呼び出し、結果判定
    print("入力パラメータチェック開始")
    if not main.checkInputParameter(input_list):
        # Falseが返却された場合、エラーメッセージをコンソールに出力して処理を終了
        eel.displayAlert(main.error_message)
        return
    print("入力パラメータチェック正常終了")
    
    # 商品タイトル一覧取得処理呼び出し(並行処理)
    print("商品タイトル一覧取得処理開始")
    main.parallelProcess("getProductTitleList", main.target_url_list)
    print("商品タイトル一覧取得処理正常終了")

    # 出品ページURL一覧取得処理呼び出し（並行処理）
    print("出品ページURL一覧取得処理開始")
    main.parallelProcess("getExhibitionPageUrlList", main.product_title_list)
    print("出品ページURL一覧取得処理正常終了")

    # 出品者情報一覧取得処理呼び出し（並行処理）
    print("出品者情報一覧取得処理開始")
    main.parallelProcess("getSellerInfoList", main.exhibition_page_url_list)
    print("出品者情報一覧取得処理正常終了")

    # CSVファイル出力処理呼び出し
    print("CSVファイル出力処理開始")
    main.outputCsv()
    print("CSVファイル出力処理正常終了")

    # 売上情報一覧取得処理呼び出し（並行処理）
    print("売上情報一覧取得処理開始")
    main.parallelProcess("getEarningsInfoList", main.yahoo_id_list)
    print("売上情報一覧取得処理正常終了")

    # CSVファイル更新処理呼び出し
    print("CSVファイル更新処理開始")
    main.updateCsv()
    print("CSVファイル更新処理正常終了")

    print("処理を終了します。")

# 画面生成処理呼び出し
desktop.start(app_name,end_point,size)