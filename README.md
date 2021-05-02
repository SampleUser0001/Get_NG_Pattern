# Get_NG_Pattern

Youtubeのコメント一覧を形態素解析し、NGにする形態素解析結果をファイルに出力する。

## 実行手順

1. app/input配下に${動画ID}.jsonファイルを配置する。
    - コメントは[GetYoutubeArchiveComment](https://github.com/SampleUser0001/GetYoutubeArchiveComment)で取得。
    - ただしツールはYoutubeの規約上、非公開。
2. docker-compose.ymlのVIDEO_IDを${動画ID}に変更する。
3. 下記実行
``` sh
docker-compose up
```

## 実行結果

app/output/${動画ID}ディレクトリ配下に出力される。

### NG条件（暫定）

下記条件をすべて満たす

1. 形態素解析結果が50行以上。
2. 形態素解析結果同士を比較したとき、類似度が0.8より大きいコメントが存在する。

## 参考

- [GetYoutubeArchiveComment](https://github.com/SampleUser0001/GetYoutubeArchiveComment)
- [Use_MeCab](https://github.com/SampleUser0001/Use_MeCab)
