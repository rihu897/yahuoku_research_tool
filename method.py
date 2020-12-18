import os
import time
import re
import threading
import urllib.parse
import urllib.request
import datetime
import io
import numpy as np
import pandas as pd
from selenium.webdriver import Firefox, FirefoxOptions
from PIL import Image

class Main:
    def __init__(self):
        # 変数定義
        self.target_url_list = []           # URLリスト
        self.ng_id_list = []                # 除外IDリスト
        self.output_directory = ""          # 結果ファイル出力先
        self.result_csv = ""                # 結果ファイルのパス
        self.threads_num = 1                # スレッド数
        self.wait_time = 0                  # 取得間隔
        self.error_message = ""             # エラーメッセージ
        self.product_title_list = []        # 商品タイトルリスト
        self.exhibition_page_url_list = []  # 出品ページURLリスト
        self.seller_info_list = []          # 出品者情報リスト
        self.yahoo_id_list = []             # Yahoo!IDリスト
        self.earnings_info_list = []        # 売上情報リスト

    ### Firefoxを起動する関数
    def setDriver(self,driver_path,headless_flg):
        # Firefoxドライバーの読み込み
        options = FirefoxOptions()

        # ヘッドレスモード（画面非表示モード）をの設定
        if headless_flg==True:
            options.add_argument('--headless')

        # 起動オプションの設定
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
        #options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--incognito')          # シークレットモードの設定を付与

        # FirefoxのWebDriverオブジェクトを作成する。
        return Firefox(executable_path=os.getcwd() + "\\" + driver_path,options=options)

    ### 入力パラメータチェック
    def checkInputParameter(self,input_list):
        # URLリストのCSVファイル存在確認
        if os.path.isfile(input_list[0]):
            # ファイルが存在する場合、CSVファイルの内容をリストに格納
            df = pd.read_csv(input_list[0])
            tmp_list = df.values.tolist()
            for url in tmp_list:
                self.target_url_list.append(url[0])
        else:
            # ファイルが存在しない場合、エラーメッセージを更新してFalseを返却
            self.error_message = "ERROR：URL一覧のCSVファイルが見つかりません path=" + input_list[0]
            return False
        # コンソールに情報を出力
        print("対象URL：" + str(self.target_url_list))

        # 除外IDリストのパスの入力確認
        if not input_list[1] == "":
            # 除外IDリストのパスが入力されている場合、CSVファイルの存在確認
            if os.path.isfile(input_list[1]):
                # ファイルが存在する場合、CSVファイルの内容をリストに格納
                df = pd.read_csv(input_list[1])
                tmp_list = df.values.tolist()
                for ng_id in tmp_list:
                    self.ng_id_list.append(ng_id[0])
            else:
                # ファイルが存在しない場合、エラーメッセージを更新してFalseを返却
                self.error_message = "ERROR：除外ID一覧のCSVファイルが見つかりません path=" + input_list[1]
                return False
            # コンソールに情報を出力
            print("除外対象Yahoo!ID：" + str(self.ng_id_list))

        # 結果出力先ディレクトリ存在確認・結果判定
        self.output_directory = input_list[2]
        if not os.path.isdir(self.output_directory):
            # ディレクトリが存在しない場合、エラーメッセージを更新してFalseを返却
            self.error_message = "ERROR：結果ファイル出力先が見つかりません 結果ファイル出力先=" + self.output_directory
            return False
        # コンソールに情報を出力
        print("結果ファイル出力先：" + self.output_directory)

        # スレッド数、取得間隔を格納
        self.threads_num = int(input_list[3])
        self.wait_time = int(input_list[4])
        # コンソールに情報を出力
        print("スレッド数：" + input_list[3])
        print("取得間隔：{}秒".format(input_list[4]))

        # Trueを返却
        return True

    ### 商品タイトル一覧取得処理
    def getProductTitleList(self, list):
        # 商品タイトル一覧
        product_title_list_parts = []
        # ドライバ起動
        driver = self.setDriver("geckodriver.exe",False)

        # URLリスト分繰り返し
        for url in list:
            # ブラウザを開き、URLにアクセス
            driver.get(url)
            time.sleep(1)

            # ページ判定
            if url.startswith("https://www.amazon.co.jp/gp/"):
                for i in range(2):
                    # ランキングページの場合
                    atag_list = driver.find_elements_by_css_selector("span > div > span > a:nth-of-type(1)")
                    for atag in atag_list:
                        # 商品名取得
                        product_title = atag.find_element_by_class_name("p13n-sc-truncate-desktop-type2").get_attribute("textContent")
                        # 商品タイトル一覧に追加
                        product_title_list_parts.append(product_title)
                        # コンソールに情報を出力
                        print(product_title)
                    # 1ページ目の場合
                    if i == 0:
                        # 次のページへのリンク
                        next_page_url = driver.find_element_by_css_selector(".a-last > a").get_attribute("href")
                        driver.get(next_page_url)
                        time.sleep(2)
            else:
                # 商品個別ページの場合
                product_title = re.sub("\n","",driver.find_element_by_id("productTitle").get_attribute("textContent"))
                # 商品タイトル一覧に追加
                product_title_list_parts.append(product_title)
                # コンソールに情報を出力
                print(product_title)
            
            # 取得間隔分待機
            time.sleep(self.wait_time)

        # ブラウザを閉じる
        driver.close()
        # 商品タイトル一覧を統合
        self.product_title_list.extend(product_title_list_parts)
        # 重複削除
        self.product_title_list = sorted(set(self.product_title_list), key=self.product_title_list.index)

    # 出品ページURL一覧取得処理
    def getExhibitionPageUrlList(self, list):
        # 出品ページURL一覧
        exhibition_page_url_list_parts = []
        # ドライバ起動
        driver = self.setDriver("geckodriver.exe",False)
        
        # リスト分繰り返し
        for title in list:
            # 検索結果URL作成
            url = "https://auctions.yahoo.co.jp/search/search?va="
            for i,word in enumerate(title.split()):
                if i < 6:
                    # URLにURLエンコードした検索文字列を追加
                    url = url + "+" + urllib.parse.quote(word)
                else:
                    # 6ワード以上の場合、ループを終了
                    break

            # ブラウザを開き、URLにアクセス
            driver.get(url)
            time.sleep(1)

            # 検索結果判定
            if len(driver.find_elements_by_css_selector("div.Notice.u-marginT5 > p > span.Notice__wandText")) == 0:
                while True:
                    # 検索結果が0件ではない場合（0件の場合はスキップ）
                    product_titlelink_list = driver.find_elements_by_class_name("Product__titleLink")
                    for product_titlelink in product_titlelink_list:
                        # 出品ページURL取得
                        exhibition_page_url = product_titlelink.get_attribute("href")
                        # 出品ページ一覧に追加
                        exhibition_page_url_list_parts.append(exhibition_page_url)
                        # コンソールに情報を出力
                        print(exhibition_page_url)
                    # トランザクション開始（※次のページの存在確認）
                    try:
                        # 次のページへのリンク
                        next_page_url = driver.find_element_by_css_selector(".Pager__list--next > a").get_attribute("href")
                        driver.get(next_page_url)
                        time.sleep(2)
                    except:
                        # 次のページが存在しない為、ループ終了
                        break
            
            # 取得間隔分待機
            time.sleep(self.wait_time)

        # ブラウザを閉じる
        driver.close()
        # 出品ページURL一覧を統合
        self.exhibition_page_url_list.extend(exhibition_page_url_list_parts)
        # 重複削除
        self.exhibition_page_url_list = sorted(set(self.exhibition_page_url_list), key=self.exhibition_page_url_list.index)

    # 出品者情報一覧取得処理
    def getSellerInfoList(self, list):
        seller_info_list_parts = [] # 出品者情報一覧
        seller_name = ""            # Yahoo!ID
        listing_num = ""            # 総出品数
        thumbnail_id = ""           # サムネイル画像のID

        # ドライバ起動
        driver = self.setDriver("geckodriver.exe",False)
        
        # リスト分繰り返し
        for url in list:
            # ブラウザを開き、URLにアクセス
            driver.get(url)
            time.sleep(1)
            
            # Yahoo!IDを取得後、出品者ページへ移動(ページ読み込み失敗対策で成功するまで無限ループ)
            seller_link = driver.find_element_by_css_selector(".Seller__name > a")
            seller_name = seller_link.get_attribute("textContent")
            seller_page_url = seller_link.get_attribute("href")
            while True:
                driver.get(seller_page_url)
                time.sleep(2)
                # 総出品数を取得
                if len(driver.find_elements_by_css_selector("#sbn > fieldset > div.sbox_1.cf > div.sbox_2 > div > select > option:nth-child(1)")) > 0:
                    listing_num = re.sub("す.*（|）","",driver.find_element_by_css_selector("#sbn > fieldset > div.sbox_1.cf > div.sbox_2 > div > select > option:nth-child(1)").get_attribute("textContent"))
                    break
                else:
                    print("ページの読み込みに失敗しました。 Yahoo!ID=" + seller_name)
                    print("ページをリロードします。")
                    print("----------------------------------------")
                    
            # サムネイル画像を保存
            try:
                thumbnail_id = seller_name + ".jpeg"
                thumbnail_url = driver.find_element_by_css_selector("#sellername > div.seller__img > img").get_attribute("src")
                f = io.BytesIO(urllib.request.urlopen(thumbnail_url).read())
                thumbnail_image = Image.open(f).convert("RGB")
                # imgディレクトリ存在確認
                if not os.path.isdir(self.output_directory + "\img"):
                    # ディレクトリが存在しない場合、新規作成
                    os.mkdir(self.output_directory + "\img")
                thumbnail_image.save(self.output_directory + "\img\\" + thumbnail_id, "JPEG", quality=95)
            except:
                # アクセスのできないサムネイル画像の場合、サムネイル画像のIDに空文字を設定
                thumbnail_id = ""

            # 出品者情報一覧に格納
            seller_info_list_parts.append([seller_name, listing_num, "", "", "", "", "", "", "", "", "", "", thumbnail_id])
            # コンソールに情報を出力
            print("Yahoo!ID："+seller_name)
            print("総出品数："+listing_num)
            print("サムネイル画像："+thumbnail_id)
            print("----------------------------------------")

            # 取得間隔分待機
            time.sleep(self.wait_time)

        # ブラウザを閉じる
        driver.close()
        # 出品者情報一覧を統合
        for seller_info in seller_info_list_parts:
            # 重複確認
            flg = True
            for i in range(len(self.seller_info_list)):
                if seller_info[0] in self.seller_info_list[i][0]:
                    flg = False
            if flg:
                # 重複がない場合、除外IDに指定されていないか確認
                if seller_info[0] not in self.ng_id_list:
                    # 出品者情報一覧に追加
                    self.seller_info_list.append(seller_info)

    # 売上情報一覧取得処理
    def getEarningsInfoList(self, list):
        earnings_info_list_parts = []   # 売上情報一覧

        # ドライバ起動
        driver = self.setDriver("geckodriver.exe",False)
        
        # リスト分繰り返し
        for id in list:
            earnings_info = [id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 売上情報
            target_date_list = []                               # 集計対象年月

            # 検索結果URL作成
            url = "http://ochisatsu.com/rating/?code=%B4%C1%BB%FA%C8%BD%CA%CC%CD%D1&U={}&SUBMIT=%B8%A1%BA%F7".format(id)
            # ブラウザを開き、URLにアクセス
            driver.get(url)
            time.sleep(2)
            
            # 現在の年月を取得
            target_date = str(datetime.datetime.now().strftime("%Y/%m"))
            
            # 集計対象年月を設定
            month = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
            target_date_list.append(target_date)
            for i in range(5):
                tmp = target_date.split("/")
                month_index = month.index(tmp[1]) - 1
                target_date = tmp[0] + "/" + month[month_index]
                target_date_list.append(target_date)
            
            flg = True
            while flg:
                # 表を取得
                tr_list = driver.find_elements_by_css_selector("body > center:nth-child(5) > p:nth-child(10) > comment > table > tbody > tr > td > table > tbody > tr")

                for tr in tr_list:
                    # 表のラベルは処理をスキップ
                    if len(tr.find_elements_by_css_selector("td:nth-child(7) > small")) == 0 or tr.find_element_by_css_selector("td:nth-child(7) > small").get_attribute("textContent") == "終了日":
                        continue
                    
                    # 終了日取得
                    end_date = tr.find_element_by_css_selector("td:nth-child(7) > small").get_attribute("textContent")[:7]

                    # 落札額取得
                    sale_amount = 0
                    if len(tr.find_elements_by_css_selector("th:nth-child(4) > small")) > 0:
                        sale_amount = re.sub(",","",tr.find_element_by_css_selector("th:nth-child(4) > small").get_attribute("textContent"))
                    else:
                        sale_amount = re.sub(",","",tr.find_element_by_css_selector("td:nth-child(4) > small").get_attribute("textContent"))
                    
                    try:
                        # 落札額をint型にキャスト
                        sale_amount = int(sale_amount)
                    except:
                        # 落札額が数値以外の場合、処理をスキップ 
                        continue

                    # 終了日判定、売上加算
                    if end_date == target_date_list[0]:
                        earnings_info[1] += 1
                        earnings_info[6] += sale_amount
                    elif end_date == target_date_list[1]:
                        earnings_info[2] += 1
                        earnings_info[7] += sale_amount
                    elif end_date == target_date_list[2]:
                        earnings_info[3] += 1
                        earnings_info[8] += sale_amount
                    elif end_date == target_date_list[3]:
                        earnings_info[4] += 1
                        earnings_info[9] += sale_amount
                    elif end_date == target_date_list[4]:
                        earnings_info[5] += 1
                        earnings_info[10] += sale_amount
                    elif end_date == target_date_list[5]:
                        flg = False
                        break
                    else:
                        continue

                # 次のページへのリンク
                next_page_links = driver.find_elements_by_css_selector("body > center:nth-child(5) > p:nth-child(9) > small > b > a")
                for next_page_link in next_page_links:
                    if "次のページ" == next_page_link.get_attribute("textContent"):
                        driver.get(next_page_link.get_attribute("href"))
                        time.sleep(3)
                        continue
                # 次のページが存在しない為、ループを終了
                break
            
            # 売上情報一覧に追加
            earnings_info_list_parts.append(earnings_info)
            # コンソールに情報を出力
            print("Yahoo!ID：" + earnings_info[0])
            for i in range(5):
                print(target_date_list[i])
                print("入札件数：{0}件  売上:{1}円".format(earnings_info[i+1], earnings_info[i+6]))
            print("----------------------------------------")
        
            # 取得間隔分待機
            time.sleep(self.wait_time)

        # ブラウザを閉じる
        driver.close()
        # 出品者情報一覧を統合
        for earnings_info in earnings_info_list_parts:
            self.earnings_info_list.append(earnings_info)

    # 並行処理
    def parallelProcess(self, func_name, list):
        thread_list = []
        # リスト分割
        split_url_list = np.array_split(list, self.threads_num)
        # スレッド準備、関数呼び出し
        for i in range(self.threads_num):
            thread = threading.Thread(target=eval("self." + func_name), args=(split_url_list[i],))
            thread_list.append(thread)
            thread.start()
        # 全スレッドの処理が完了するまで待機
        for thread in thread_list:
            thread.join()

    # CSVファイル出力処理
    def outputCsv(self):
        dt_now = datetime.datetime.now()    # 現在時刻
        self.result_csv = self.output_directory + "\\{}.csv".format(dt_now.strftime("%Y%m%d_%H%M%S")) # 出力ファイルのパス
        # CSV出力
        df = pd.DataFrame(self.seller_info_list, columns = ["Yahoo!ID", "出品数", "入札件数①", "入札件数②", "入札件数③", "入札件数④", "入札件数⑤", "売上①", "売上②", "売上③", "売上④", "売上⑤", "画像ID"])
        df.to_csv(self.result_csv, index=False)
        # コンソールに情報を出力
        print("出力ファイル：" + self.result_csv)
        # Yahoo!IDリストを更新
        self.yahoo_id_list = df["Yahoo!ID"].values.tolist()

    # CSVファイル更新処理
    def updateCsv(self):
        # CSV読み込み
        df = pd.read_csv(self.result_csv)
        tmp_list = df.values.tolist()
        # 入札件数、売り上げを更新
        for earnings_info in self.earnings_info_list:
            for tmp in tmp_list:
                if tmp[0] == earnings_info[0]:
                    # Yahoo!IDが一致する行を更新
                    for i in range(10):
                        tmp[i + 2] = earnings_info[i + 1]

        # データフレーム更新
        df = pd.DataFrame(tmp_list, columns = ["Yahoo!ID", "出品数", "入札件数①", "入札件数②", "入札件数③", "入札件数④", "入札件数⑤", "売上①", "売上②", "売上③", "売上④", "売上⑤", "画像ID"])
        
        # CSV出力
        df.to_csv(self.result_csv, index=False)
        # コンソールに情報を出力
        print("更新ファイル：" + self.result_csv)