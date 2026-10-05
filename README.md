# Meta Book Reader（iOS試作）

Ray-Ban Metaで見ている本のページを読み取り、指定文字数以内の日本語要約を音声で読み上げるアプリです。
ソースとXcodeプロジェクトを用意しました。Linux環境で作成したため、Xcodeビルド・実機検証・実際のAPI通信は未実施です。

## 動作

1. Meta AIアプリでメガネをペアリングし、Developer Modeを有効にする。
2. このアプリの設定にご自身のOpenAI APIキーを保存する。
3. 「メガネを接続」で登録し、「接続を開始」「映像を開始」を順に押す。
4. 本を明るい場所で正面に向け、映像に読みたい文章がはっきり写ることを確認する。
5. 要約の上限文字数を設定して「このページを要約」を押す。
6. 要約が表示され、日本語で読み上げる。「もう一度聴く」「読み上げ停止」も使用可能。

初期値は200文字、設定範囲は50〜1000文字です。句読点を含み、SwiftのString.count（見た目の文字単位）で数えます。
AIの結果が長すぎる場合は1回だけ再要約し、まだ長ければ文末または上限手前で切って制限を守ります。
文字を十分に読めない場合は再撮影を案内します。読み取り・要約の正確さは実際の本と照合してください。

## Macで開く

公式の現在のCameraAccessサンプルに合わせ、Xcode 26.4以上、Swift 6.3以上、iOS 17.2以上を想定しています。
DAT SDKはSwift Package Managerで1.0.0に固定しました。Xcodeで依存解決が必要です。

1. このフォルダをMacへコピーする。
2. MetaBookReader.xcodeprojをXcodeで開く。
3. Signing & Capabilitiesでご自身のTeamを選び、Bundle Identifierを固有の値に変更する。
4. 実機iPhoneを選び、ビルドして実行する。

プロジェクトを再生成する場合：`python3 generate_project.py`
XcodeGenを使う場合は代わりに`xcodegen generate`でproject.ymlから生成できます。

Developer Modeでの試作ではMETA_APP_IDを0にしています。テスト配布・本番ではWearables Developer Centerに登録し、
META_APP_ID、CLIENT_TOKEN、DEVELOPMENT_TEAMを設定し、対応するリリースチャネルとSDK利用条件を確認してください。

## 構成と統合元

- メガネの登録・セッション・映像：Meta公式CameraAccessサンプルのViewModelsとMediaを取り込み。
- 本の要約：TurboMetaのVisionAPIServiceの画像付きChat Completions構造を改変し、OpenAIに接続。
- 日本語読み上げ：AVSpeechSynthesizer。別のクラウドTTSは不要。
- APIキー：Keychain。ソース、UserDefaults、ログへの保存はしません。
- オリジナル画面：本の要約、文字数上限、再生・停止、キャンセル、読み取り失敗表示。

公式から取り込んだ録画・撮影の内部処理は依存関係を保つため同梱していますが、この画面から録画は開始しません。
映像設定のみ本文の読み取り向けにhigh／7fpsへ変更しました。

画像は要約ボタンを押した時点の最新のプレビューフレームです。ページ全体や本全体を連続で取り込む機能ではありません。
画像が届いていても、文字が小さい、揺れている、反射がある場合は読めないことがあります。
通常はAPI呼び出し1回、文字数を超えた場合は最大2回です。OpenAI API利用料金が発生します。

## 音声・バックグラウンド

音声はiPhoneの現在の音声出力先に再生します。メガネから聴く場合はiOSの音声出力先をメガネにしてください。
自動的なメガネへの出力固定は実装していません。
アプリがバックグラウンドに入ると解析・読み上げをキャンセルし、公式サンプルの処理で映像セッションを停止します。
戻ったら接続と映像を再開してください。ロック中の継続利用やHey Meta起動は未実装です。
停止後に古いリクエストが完了しても読み上げを再開しないよう、キャンセルとリクエストIDで管理します。

## データと公開

要約対象の画像をHTTPSでOpenAIへ送信します。OpenAI側のデータ取り扱いは同社のAPI利用条件に従います。
このアプリは画像・本文をファイル保存せず、要約と対象画像をメモリに保持します。
公式SDK側のデータ収集はSDKの設定・規約に従います。
個人のAPIキーによる試作です。一般公開する場合はバックエンド経由の認証・課金管理へ変更してください。

## 実機確認

- 登録、カメラ許可、許可拒否、メガネ未接続からの再試行。
- 明瞭な日本語の本、縦書き、見開き、ぼけた画像で読み取り結果を原文と照合。
- 50／200／1000文字の設定で表示・読み上げが同じ内容で上限以内になること。
- APIキー未設定・無効、ネットワーク断、利用上限時にエラーが見えること。
- 解析中のキャンセル、映像停止、バックグラウンド移行で遅れた読み上げが発生しないこと。
- 再生・停止・再生の操作と、メガネへのBluetooth音声出力。

## 出典・ライセンス

- [Meta公式iOS SDK](https://github.com/facebook/meta-wearables-dat-ios)
  - 取得時のGit tree SHA：122fd163cc5733ecc4af7494b003f833fed16dd5
  - [CameraAccessサンプル](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess)
  - Meta Wearables Developer Termsが適用されます。Licenses/Meta.txtを同梱。
- [TurboMeta](https://github.com/Turbo1123/turbometa-rayban-ai)
  - 取得時のGit tree SHA：78ea2f38530384ce9621e8a9a4d96b7cbc94889e
  - MIT License、Copyright (c) 2025 Turbo1123。Licenses/TurboMeta.txtを同梱。

Metaのソース・SDKを含むため、プロジェクト全体をMITライセンスと扱わないでください。
