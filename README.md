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
```
    ターゲットタグ: mysql-server  
    ソースIP の範囲： 0.0.0.0/0  
    プロトコルとポート： tcp:3306
```

3. MySQLをインストール  
1 で作成した VMインスタンス に ssh で接続し、DBを構築する
```
$ sudo rpm -Uvh http://dev.mysql.com/get/mysql-community-release-el7-5.noarch.rpm
$ sudo yum -y install mysql-community-server
$ sudo /usr/bin/systemctl start mysqld
$ sudo mysql_secure_installation
$ mysql -u root -p
Enter password: # パスワードを入力 
mysql> create database [DB_NAME];
```

## Cloud Run
1. Cloud Build and Cloud Run API を有効にする
2. [Cloud SDK](https://cloud.google.com/sdk/docs?hl=ja) をインストール
3. コンポーネントを更新する
```
$ gcloud components update
```
4. サンプルプログラム(cloud-run/todos/db.py)のDB接続先を変更する。
```python:db.py
SQLALCHEMY_DATABASE_URI = "mysql://user:password@mysqlserver/db"
```
5. サンプルアプリのテーブルを作成
```
$ cd cloud-run/todos
$ python db.py
```
6. アプリをコンテナ化して Container Registry にアップロードする
```
$ cd gcp_study01/cloud-run/todos
$ gcloud builds submit --tag gcr.io/[PROJECT-ID]/gcp_study01
```
7. Cloud Run へデプロイ
```
gcloud run deploy --image gcr.io/[PROJECT-ID]/gcp_study01 --platform managed
```

## App Engine
1. 静的ウェブサイトの作成  

GAEのルートディレクトリはプロジェクトIDにする必要があるため、`project-id`ディレクトリ名をプロジェクトIDに変更する。
```
$ cd gcp_study01/gae
$ mv project-id [PROJECT-ID]
```
2. HTML(www/index.html)内のAPI呼び出しを行っている箇所の URL を変更  
`[API-URL]`に、`Cloud Run`のサービスの詳細に表示されたURLを設定する。
```html:index.html
https://[API-URL]/todos
```
3. App Engine へデプロイ
```
$ cd [PROJECT-ID]
$ gcloud app deploy
```