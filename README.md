# Code Review Quest 🎮

バグ発見・設計レビューの思考プロセスをゲーム化し、若手エンジニアが楽しく学べるWebアプリケーション

## 🎯 概要

Code Review Questは、実際のコードレビュー業務で必要なスキルを、ゲーム形式で楽しく学習できるプラットフォームです。

### 主な機能
- 🔍 **バグ発見チャレンジ**: Pythonコードからバグを見つけるゲーム
- 📊 **スキル分析**: 弱点カテゴリの可視化とスコア管理
- 🏆 **バッジシステム**: 達成度に応じた報酬システム
- 📈 **ダッシュボード**: 学習進捗の追跡

## 🏗️ アーキテクチャ

```
Frontend (React + TypeScript) ←→ Backend (FastAPI) ←→ Worker (Code Analysis)
                                        ↓
                                   Database (PostgreSQL)
```

## 🚀 クイックスタート

### 前提条件
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### ローカル開発環境の起動

```bash
# 1. リポジトリをクローン
git clone <repository-url>
cd code-review-quest

# 2. 環境変数を設定
cp .env.example .env

# 3. 全サービスを起動
make dev

# 4. ブラウザでアクセス
open http://localhost:3000
```

## 📁 プロジェクト構造

```
code-review-quest/
├── frontend/          # React SPA (TypeScript)
├── backend/           # FastAPI サーバー
├── worker/            # コード解析ワーカー
├── problems/          # 問題データ
├── infrastructure/    # AWS CDK (IaC)
└── docs/             # 設計ドキュメント
```

## 🛠️ 開発コマンド

```bash
# 開発環境起動
make dev

# テスト実行
make test

# リント実行
make lint

# ビルド
make build

# データベース初期化
make seed-db
```

## 🌐 デプロイ

### AWS環境へのデプロイ

```bash
# CDKでインフラをデプロイ
cd infrastructure
cdk deploy --all
```

## 📖 ドキュメント

- [アーキテクチャ設計](./docs/architecture.md)
- [API仕様](./docs/api_spec.md)
- [開発ガイド](./docs/development.md)

## 🤝 コントリビューション

1. Forkしてブランチを作成
2. 変更を実装
3. テストを追加・実行
4. Pull Requestを作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](./LICENSE) を参照

## 🎮 ゲームの遊び方

1. **ログイン**: ゲストまたはSNSアカウントでログイン
2. **難易度選択**: 初級・中級・上級から選択
3. **チャレンジ開始**: 5-15分の制限時間でバグを発見
4. **結果確認**: スコアと解説、獲得バッジを確認
5. **成長追跡**: ダッシュボードで学習進捗を確認

---

**Happy Coding & Happy Learning! 🚀**
