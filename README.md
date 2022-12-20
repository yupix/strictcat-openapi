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

python main.py
```
