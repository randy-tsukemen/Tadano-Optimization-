# 提出用ファイルの作成方法

## 0. Docker環境を構築する

- <a href="https://signate.jp/competitions/428#Information1">https://signate.jp/competitions/428#Information1</a>に従う.

## 1. クレーンシミュレータを制御するためのAgentを実装する

- 以下のように"agent.py"にAgentを実装する.
  - `Agent`クラスには次のメソッドが実装されている必要がある: `get_model`, `set_params`, `policy`.
    - `get_model`メソッドではAgentのインスタンスを作成し, 使われているならばモデルファイルを読み込む.
    - `set_params`メソッドでは以下の'senkai_target_angle', 'weight_t', 'wire_ratio'のようなパラメータを読み込む.

      |  名前  |  データ型  |  単位  |  範囲  |  デフォルト  |  説明  |
      | ---- | :----: | :----: | :----: | :----: | ---- |
      |  senkai_target_angle  |  float  |  deg  |  0 ~ 180  |  -  |  目標とする旋回角度  |
      |  weight_t  |  float  |  t  |  0 ~ 4  |  1  |  吊り荷重さ(フックは除く)  |
      |  wire_ratio  |  float  |  -  |  0.1 ~ 0.9  |  0.8  |  ブームトップから地面までの距離の割合  |
      |  init_kifuku_deg  |  float  |  deg  |  10 ~ 80  |  60  |  起伏角度 初期値  |
      |  init_yure_senkai_m  |  float  |  m  |  -1 ~ 1  |  0  |  円周方向の荷揺れ 初期値  |
      |  init_yure_kifuku_m  |  float  |  m  |  -1 ~ 1  |  0  |  半径方向の荷揺れ 初期値  |
      |  param_randomize_seed  |  uint  |  -  |  -  |  0  |  内部パラメータのランダマイズ設定(== 0 : seed is not fixed)  |

    - `policy`メソッドでは観測値が渡されて次のレバー値を返す. 観測値一覧は以下. レバー値のとりうる値の範囲は0~1.

      |  名前  |  データ型  |  単位  |  説明  |
      | ---- | :----: | :----: | ---- |
      |  step  |  uint  |  -  |  シミュレーションの実行ステップ数  |
      |  turning_lever_value  |  float  |  -  |  旋回レバー操作量  |
      |  turning_encoder_angle_deg  |  float  |  deg  |  旋回エンコーダ角度  |
      |  turning_encoder_acquisition_time  |  float  |  ms  |  旋回エンコーダ取得時刻  |
      |  working_radius_m  |  float  |  m  |  作業半径  |
      |  actual_load_t  |  float  |  t  |  実荷重  |
      |  main_wire_length_m  |  float  |  m  |  主巻吊荷長さ  |
      |  boom_top_x_m  |  float  |  m  |  ブームトップのx座標  |
      |  boom_top_y_m  |  float  |  m  |  ブームトップのy座標  |
      |  boom_top_z_m  |  float  |  m  |  ブームトップのz座標  |
      |  boom_top_status  |  uint  |  -  |  座標更新時 = 1, 非更新時 = 0. 値は10Hzごとに更新される.  |
      |  left_turning_pressure_mpa  |  float  |  MPa  |  左旋回圧力  |
      |  right_turning_pressure_mpa  |  float  |  MPa  |  右旋回圧力  |
      |  tawami_diff_deg  |  float  |  deg  |  円周方向のたわみ量  |
      |  hook_x_m  |  float  |  m  |  フック先端のx座標  |
      |  hook_y_m  |  float  |  m  |  フック先端のy座標  |
      |  hook_z_m  |  float  |  m  |  フック先端のz座標  |
      |  hook_status  |  uint  |  -  |  座標更新時 = 1, 非更新時 = 0. 値は10Hzごとに更新される.  |
      |  hook_diff_c_m  |  float  |  m  |  円周方向の荷揺れ量  |
      |  hook_diff_r_m  |  float  |  m  |  半径方向の荷揺れ量  |

  - "agent.py"以外のpyファイルを作成して"agent.py"内で使用する(`import`するなど)ことも可能.

```py
class Agent(object):
    def __init__(self, action_range):
        self.model = None
        self.action_range = action_range

    @classmethod
    def get_model(cls, model_path):
        action_range = (0.0, 1.0)
        agent = cls(action_range)

        # load some model
        # e.g. agent.model = load_model(model_path)

        return agent

    def set_params(self, params):
        ...
        self.params = params

    def policy(self, observation):
        ...

        return next_lever_value
```

- もし利用したならばモデルファイルは"model"ディレクトリに保存する.
  - `Agent`クラスの`get_model`メソッドはこのディレクトリからモデルファイルを読み込むことを想定している.
- アルゴリズムを動作させるために追加で必要なPythonライブラリなどを"requirements.txt"に記述する.

## 2. 実装した制御アルゴリズムを実行する

- ターミナルで以下のコマンドを実行すると制御結果が"output/control_results.json"に保存される.
  
  ```bash
  python run.py
  ```

  - シミュレーションが走るとまずシミュレータがインスタンス化される. 続いて`get_model`メソッドが呼ばれてagentがインスタンス化され, `set_params`メソッドによってクレーンのパラメータや外的なパラメータが読み込まれる.
  - 各ステップにおいて, シミュレータから観測値が生成され, `policy`メソッドにそれが渡されて次の入力レバー値が返される. そのレバー値がシミュレータに渡されてまた新たな観測値が生成される. この一連のやり取りが`done`フラグが`True`になるまで繰り返し実行される.
  - エピソードは, 入力レバー値が1000ステップの間0になるか合計ステップ数が100000以上になると終了する(`done`フラグが`True`になる).
  - 条件やシミュレータのパラメータを変更したい場合は, 以下の"configs/sim_params.json"や"configs/external_params.json"を編集する.
    - "configs/sim_params.json"

      ```json
      {
        "param_init": 
          {
            "use_gui": false,
            "noise_randomize_seed": 0
          },
        "state_init":
          {
            "init_kifuku": 60.0,
            "weight_t": 1.0,
            "wire_ratio": 0.8,
            "init_yure_senkai_m": 0.0,
            "init_yure_kifuku_m": 0.0,
            "param_randomize_seed": 0
          }
      }
      ```

    - "configs/external_params.json"

      ```json
      {
        "senkai_target_angle": 180
      }
      ```

- ターミナルで以下のコマンドを実行すると出力された"output/control_results.json"に対する精度評価が行われ, 実装したアルゴリズムの精度を確認することができる(評価方法の詳細は https://signate.jp/competitions/428#evaluation を参照すること).

  ```bash
  python evaluate.py
  ```

  - 以下の評価結果が出力される.
    - Validation: 以下の条件を満たしていなければスコアは0となる.
      - max angular acceleration
      - max runtime per step
      - senkai distance (最後の1000ステップの平均)
    - Evaluation: 以下の各項目の評価値.
      - senkai error (最後の1000ステップの平均)
      - hook displacement error (最後の1000ステップの平均)
      - total steps (最後の1000ステップは含まない)
    - Score: 最終的なスコア.

## 3. 提出用のファイルを作成する

- 提出用ファイルのディレクトリ構造は以下のようにしなければならない.

  ```bash
  .
  ├── model              必須: 学習済みモデルが格納されるディレクトリ(空でも必要)
  │   └── ...
  ├── src                必須: .pyファイル等が格納されるディレクトリ
  │   ├── agent.py       必須: Agentが実装された.pyファイル
  │   └── ...            オプション: 他に必要なファイルやディレクトリ(.py, .json, 等)
  └── requirements.txt   オプション: 追加で必要なPythonライブラリのリスト
  ```

- 上記をzipで圧縮する.
  - ターミナルで以下のコマンドを実行すると"submit.zip"という名前で提出用ファイルが作成される.

    ```bash
    bash submit.sh
    ```

- ファイルを投稿してから結果が返るまで暫く時間がかかる.
