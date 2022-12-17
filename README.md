# 初めに

このプロジェクトはstrictcatという型安全にRESTFul APIを使用するためのプロジェクトのスキーマをOpenAPIから生成するためのプロジェクトです。
極めて幼稚な実装になっているため、OpenAPIの仕様全てを網羅しているわけではないことをあらかじめご了承ください。これをサポートしてほしいというのがあればサポートします。

## 使い方

```bash
pip install -r requirements.txt
mv .env.example .env

# .envの中にある変数にOpenAPIがあるurlを入れてください

python main.py
```
