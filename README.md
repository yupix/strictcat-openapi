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

## USE_DEFAULT_VALUEについて

default値が設定されている場合それを型として使用するオプションです。
例えば以下のようなスキーマを次のような型に変更します。

### 注意事項

- この機能はbodyやparams,queryには適応されません
    - 主にエラー等といった明らかにそれしか入らないといった場合を目的として作成している機能の為です。
- この機能はまだ追加されて日数が経っていないため、不具合がある可能性があります

```json
{
    "ALREADY_USED_USERNAME_ERROR": {
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "example": "58ee27a1-f431-4e6f-9656-666ed857d9bc",
                "default": "58ee27a1-f431-4e6f-9656-666ed857d9bc"
            },
            "type": {
                "type": "string",
                "example": "failed",
                "default": "failed"
            },
            "code": {
                "type": "string",
                "example": "ALREADY_USED_USERNAME",
                "default": "ALREADY_USED_USERNAME"
            },
            "message": {
                "type": "string",
                "example": "既に利用されているユーザー名です",
                "default": "既に利用されているユーザー名です"
            }
        },
        "required": [
            "id",
            "type",
            "code",
            "message"
        ]
    }
}
```

```ts
export interface ALREADY_USED_USERNAME_ERROR {id: '58ee27a1-f431-4e6f-9656-666ed857d9bc', type: 'failed', code: 'ALREADY_USED_USERNAME', message: '既に利用されているユーザー名です'}
```

## 組み込みに使いたい方向けの情報

このプロジェクトを使用する場合の主な用途として、バックエンドとフロントエンドとのAPI通信を円滑にするというものがあると思いますが、そのうえでこのプロジェクトをサブモジュールにするのも1つの手ではありますが、作者の私(yupix)的なお勧めは`pyinstaller`を用いてバイナリを作成し、それをフロントエンド側に用意することです。以下にpyinstallerを用いたバイナリの作成コマンドを載せておきます。

```bash
pip install pyinstaller
pyinstaller main.py --onefile --noconsole --clean
```

出力先はdistの中の`main`または`main.exe`などになると思います
