$(function() {

  // Start!ボタンクリック時
  $("#start_button").click(function() {
    // 入力値取得
    let input_list = [url_list_path.value, ng_id_list_path.value, output_directory.value, thread_num.value, wait_time.value]
    // 入力値チェック
    if (input_list[0] == "") {
      alert("ERROR：URL一覧のCSVファイルパスが入力されていません");
    } else if ('.csv' != input_list[0].slice(-4)) {
      alert("ERROR：URL一覧のファイルの拡張子が不正です。 path=" + input_list[0]);
    } else if ('.csv' != input_list[1].slice(-4) && input_list[1].length > 0) {
      alert("ERROR：除外ID一覧のファイルの拡張子が不正です。 path=" + input_list[1]);
    } else if (input_list[2] == "") {
      alert("ERROR：結果ファイル出力先ディレクトリが入力されていません");
    } else {
      // 商品情報抽出処理呼び出し
      eel.startYahuokuResearch(input_list);
    }
  });

  // アラート表示処理
  eel.expose(displayAlert)
  function displayAlert(alert_txt) {
    alert(alert_txt);
  }
});