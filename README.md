# GCPの無料枠(Always Free)を利用してWebサービスを構築する方法
## 利用するGCPのサービス
- Compute Engine 
  - Cloud SQL に無料枠がないため、DBサーバー(MySQL)として使用する。
  - f1-micro インスタンス上に MySQL のイメージをデプロイしたところ正常動作しなかったので、今回は GCE 上に直接インストールする。
- Cloud Run
  - FastAPI(Python) で作成した API を動かすために使用
- App Engine
  - 静的ファイルのホスティングに使用
- Cloud Storage (今回は未使用)
  - 静的ファイルのホスティングに使用しようとしたが、独自ドメインでSSLホスティングするのがちょっと面倒そうだったので今回は使用しない。

## Compute Engine
1. VMインスタンスを作成  
```
リージョン：us-west1 (us-central1, us-east1でも可)  
マシンタイプ：f1-micro（vCPU x 1、メモリ 0.6 GB）  
OS： CentOS 7  
ブートディスクの種類：標準の永続ディスク  
ブートディスクのサイズ：30GB  
ネットワークタグ: mysql-server
```

2. ファイアウォール ルール  
    ターゲットタグ: mysql-server  
    ソースIP の範囲： 0.0.0.0/0  
    プロトコルとポート： tcp:3306

3. MySQLをインストール  
```
$ sudo rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el7-5.noarch.rpm
$ sudo yum -y install mysql-community-server
$ sudo /usr/bin/systemctl start mysqld
$ sudo mysql_secure_installation
```

## Cloud Run
1. Cloud Build and Cloud Run API を有効にする
2. [Cloud SDK](https://cloud.google.com/sdk/docs?hl=ja) をインストール
3. コンポーネントを更新する
```
$ gcloud components update
```
4. db.py の接続先を変更する。
```
SQLALCHEMY_DATABASE_URI = "mysql://user:password@mysqlserver/db"
```
5. アプリをコンテナ化して Container Registry にアップロードする
```
$ cd gcp_study01/cloud-run/todos
$ gcloud builds submit --tag gcr.io/[PROJECT-ID]/gcp_study01
```
6. Cloud Run へデプロイ
```
gcloud run deploy --image gcr.io/[PROJECT-ID]/gcp_study01 --platform managed
```

## App Engine
1. 静的ウェブサイトの作成
```
$ cd gcp_study01/gae
$ mv project-id [PROJECT-ID]
```
2. API の URL を 変更
```
https://[API-URL]/todos
```
3. App Engine へデプロイ
```
$ cd [PROJECT-ID]
$ gcloud app deploy
```