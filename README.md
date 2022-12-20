# 初めに

このプロジェクトはstrictcatという型安全にRESTFul APIを使用するためのプロジェクトのスキーマをOpenAPIから生成するためのプロジェクトです。
極めて幼稚な実装になっているため、OpenAPIの仕様全てを網羅しているわけではないことをあらかじめご了承ください。これをサポートしてほしいというのがあればサポートします。

## 設定について(.envファイル)

|設定名|設定例|説明|
|---|---|---|
|OPENAPI_URL|https://example.com/open-api.json|OpenAPIが公開されているUrlを指定できます|
|USE_EXPORT|true|typeやinterfaceをexportするかどうかの設定です(.d.tsなどにschemaを書く際にお勧めです)|

## 使い方

```bash
pip install -r requirements.txt
mv .env.example .env

# .envの中にある変数にOpenAPIがあるurlを入れてください

python main.py -e ./.env
```

## 組み込みに使いたい方向けの情報

このプロジェクトを使用する場合の主な用途として、バックエンドとフロントエンドとのAPI通信を円滑にするというものがあると思いますが、そのうえでこのプロジェクトをサブモジュールにするのも1つの手ではありますが、作者の私(yupix)的なお勧めは`pyinstaller`を用いてバイナリを作成し、それをフロントエンド側に用意することです。以下にpyinstallerを用いたバイナリの作成コマンドを載せておきます。

```bash
pip install pyinstaller
pyinstaller main.py --onefile --noconsole --clean
```

出力先はdistの中の`main`または`main.exe`などになると思います
