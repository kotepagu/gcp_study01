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
以下の内容でVMインスタンスを作成する。（特に指定がない項目はデフォルト値のまま）
```
名前：任意のインスタンス名
リージョン：us-west1 (us-central1, us-east1でも可)  
ゾーン：任意のゾーン
マシンタイプ：f1-micro（vCPU x 1、メモリ 0.6 GB）  
OS： CentOS 7  
ブートディスクの種類：標準の永続ディスク  
ブートディスクのサイズ：30GB  
ネットワークタグ: mysql-server
```

2. ファイアウォール ルール  
APIからMySQLに接続できるようにファイアウォールルールを作成する。
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
Enter current password for root (enter for none): # 何も入力せずにリターンキーを押す
Set root password? [Y/n] # Yを入力
New password: # 任意のパスワードを入力
Re-enter new password: #上と同じパスワードを入力
Remove anonymous users? [Y/n] # Yを入力
Disallow root login remotely? [Y/n] # Yを入力
Remove test database and access to it? [Y/n]  # Yを入力
Reload privilege tables now? [Y/n] # Yを入力
$ mysql -u root -p
Enter password: # root のパスワードを入力 
mysql> create database gcp_study;
mysql> CREATE USER gcp_study IDENTIFIED BY '[任意のパスワード]';
mysql> GRANT ALL PRIVILEGES ON *.* TO 'gcp_study'@'%';
```

## Cloud Run
1. Cloud Build and Cloud Run API を有効にする
2. Cloud Shell をアクティブにし、サンプルプログラムをクローンする
```
$ git clone https://github.com/kotepagu/gcp_study01.git
```
3. サンプルプログラム(cloud-run/todos/db.py)のDB接続先を変更する。
```
$ cd gcp_study01/cloud-run/todos
$ vi db.py
  ・・・
  SQLALCHEMY_DATABASE_URI = "mysql://user:password@mysqlserver/db"
  ↓ 例) MySQLをインストールしたVMインスタンスの外部IPが「1.2.3.4」、gcp_studyのパスワードが'pass'の場合
  SQLALCHEMY_DATABASE_URI = "mysql://gcp_study:pass@1.2.3.4/gcp_study"
  ・・・
```
4. サンプルアプリのテーブルを作成
```
$ docker build -t gcp_study .
$ docker run --rm gcp_study python db.py
```
5. アプリをコンテナ化して Container Registry にアップロードする
```
$ gcloud builds submit --tag gcr.io/[PROJECT-ID]/gcp_study01
```
6. Cloud Run へデプロイ
```
gcloud run deploy --image gcr.io/[PROJECT-ID]/gcp_study01 --platform managed
Service name (gcpstudy01): # 任意のサービス名(そのままリターンだと`gcpstudy01`というサービス名になる)
Please specify a region:
・・・
 [9] us-west1
・・・
Please enter your numeric choice: # 9を入力
Allow unauthenticated invocations to [gcpstudy01] (y/N)? # yを入力
```

## App Engine
1. HTML(www/index.html)内のAPI呼び出しを行っている箇所の URL を変更  
`[API-URL]`に、`Cloud Run`のサービスの詳細に表示されたURLを設定する。
```html:index.html
$ cd ~/gcp_study01/gae
$ vi www/index.html
・・・
axios.get('https://[API-URL]/todos/')
・・・
```
3. App Engine へデプロイ
```
$ gcloud app deploy
Services to deploy:
・・・
Do you want to continue (Y/n)? # yを入力

```