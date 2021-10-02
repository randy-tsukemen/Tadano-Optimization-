# How to Make the File for Submission

## 0. Set up the Docker Environment

- Follow <a href="https://signate.jp/competitions/428#Information1">https://signate.jp/competitions/428#Information1</a>.

## 1. Implement the Agent for Controlling the Crane Simulator

- Implement the agent in "agent.py" as follows.
  - `Agent` class must have the following methods: `get_model`, `set_params`, and `policy`.
    - `get_model` instanciates the agent and loads some model if used.
    - `set_params` sets parameters such as 'senkai_target_angle', 'weight_t', 'wire_ratio', etc. as follows.

      |  name  |  type  |  unit  |  range  |  default  |  description  |
      | ---- | :----: | :----: | :----: | :----: | ---- |
      |  senkai_target_angle  |  float  |  deg  |  0 ~ 180  |  -  |  Target angle from the starting point  |
      |  weight_t  |  float  |  t  |  0 ~ 4  |  1  |  Weight of the hanging load  |
      |  wire_ratio  |  float  |  -  |  0.1 ~ 0.9  |  0.8  |  The length of the wire  |
      |  init_kifuku_deg  |  float  |  deg  |  10 ~ 80  |  60  |  Initial value of the ups and downs angle  |
      |  init_yure_senkai_m  |  float  |  m  |  -1 ~ 1  |  0  |  Load swing initial value of the radial direction  |
      |  init_yure_kifuku_m  |  float  |  m  |  -1 ~ 1  |  0  |  Load swing initial value of the circumference direction  |
      |  param_randomize_seed  |  uint  |  -  |  -  |  0  |  Randomize seed of the internal parameter(== 0 : seed is not fixed)  |

    - `policy` returns the next lever value after the observations are passed. The observations are as follows. The next lever value should range from 0 to 1.

      |  name  |  type  |  unit  |  description  |
      | ---- | :----: | :----: | ---- |
      |  step  |  uint  |  -  |  The practice step count of simulation  |
      |  turning_lever_value  |  float  |  -  |  Turning lever operation quantity  |
      |  turning_encoder_angle_deg  |  float  |  deg  |  Turning encoder angle  |
      |  turning_encoder_acquisition_time  |  float  |  ms  |  The turning encoder acquisition time  |
      |  working_radius_m  |  float  |  m  |  Work radius  |
      |  actual_load_t  |  float  |  t  |  Weight of the actual load  |
      |  main_wire_length_m  |  float  |  m  |  The length of the wire  |
      |  boom_top_x_m  |  float  |  m  |  x coordinate of the boom top  |
      |  boom_top_y_m  |  float  |  m  |  y coordinate of the boom top  |
      |  boom_top_z_m  |  float  |  m  |  z coordinate of the boom top  |
      |  boom_top_status  |  uint  |  -  |  When values are updated = 1, not updated = 0. The value is updated at 10Hz.  |
      |  left_turning_pressure_mpa  |  float  |  MPa  |  Pressure of the left turning  |
      |  right_turning_pressure_mpa  |  float  |  MPa  |  Pressure of the right turning  |
      |  tawami_diff_deg  |  float  |  deg  |  Flection of the circumference direction  |
      |  hook_x_m  |  float  |  m  |  x coordinate of the hook  |
      |  hook_y_m  |  float  |  m  |  y coordinate of the hook  |
      |  hook_z_m  |  float  |  m  |  z coordinate of the hook  |
      |  hook_status  |  uint  |  -  |  When values are updated = 1, not updated = 0. The value is updated at 10Hz.  |
      |  hook_diff_c_m  |  float  |  m  |  Load swing of the circumference direction  |
      |  hook_diff_r_m  |  float  |  m  |  Load swing of the radial direction  |

  - You can make .py files other than "agent.py" and use them in "agent.py".

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

- Save the model files in "model" directory if used.
  - `get_model` method in `Agent` class is assumed to load the model files from the directory.
- List some additional libraries in "requirements.txt" if necessary.

## 2. Run the Crane Simulator with the Agent

- Execute the following command in the terminal and the output will be saved in "output/control_results.json"
  
  ```bash
  python run.py
  ```

  - When the simulation runs, the simulator is instanciated at first. Then `get_model` is called to instanciate the agent, and `set_params` is called to set  the parameters from the passed parameters.
  - In each step, observations are generated from the simulator and passed to `policy` and the next lever value is returned, then passed to the simulator, and so on, until `done` flag will be `True`(while `done` flag is `False`).
  - An episode terminates(`done` flag will be `True`) when the lever value remains 0 for 1000 steps, or the total steps is greater than or equal to 100000.
  - If you want to change conditions or parameters for simulator, modify "configs/sim_params.json" or "configs/external_params.json"
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

- Execute the following command in the terminal and the evaluation for "output/control_results.json" will be made and you can see how well your algorithm performed (see also https://signate.jp/competitions/428#evaluation for more information about the evaluation).

  ```bash
  python evaluate.py
  ```

  - You can see the evaluation results as follows.
    - Validation: The score will be 0 if the following conditions are not satisfied.
      - max angular acceleration
      - max runtime per step
      - senkai distance (mean of the last 1000 steps)
    - Evaluation: The score for the following items.
      - senkai error (mean of the last 1000 steps)
      - hook displacement error (mean of the last 1000 steps)
      - total steps (the last 1000 steps not included)
    - Score: The overall score.

## 3. Make the File for Submission

- The directory structure of files for submission must be as follows.

  ```bash
  .
  ├── model              required: directory where the trained model files are put (leave it empty if not used)
  │   └── ...
  ├── src                required: directory where .py files are put
  │   ├── agent.py       required: .py file in which the agent is implemented
  │   └── ...            optional: some other files or directories(.py, .json, etc.)
  └── requirements.txt   optional: list of some additional libraries necessary for the algorithm to work
  ```

- Compress the files above in a zip file.
  - Excecute the following command in the terminal and the file for submission("submit.zip") will be created.

    ```bash
    bash submit.sh
    ```

- It may take some time to get the result after you submit the file.
