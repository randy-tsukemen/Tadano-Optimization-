import gym
import numpy as np
import json
import TDN_CraneSim_PyIF

class CraneEnv(gym.Env):
    def __init__(self, env_params, sim_params):
        param_init = sim_params['param_init']
        state_init = sim_params['state_init']

        ob_spaces = {}
        for available_state in env_params['available_states']:
            if available_state in {'step', 'turning_encoder_acquisition_time', 'working_radius_m', 'actual_load_t', 'main_wire_length_m'}:
                ob_spaces[available_state] = gym.spaces.Box(low = 0, high = float('inf'), shape = ())
            elif available_state in {'hook_status', 'boomtop_status'}:
                ob_spaces[available_state] = gym.spaces.Discrete(2)
            elif available_state == 'turning_lever_value':
                ob_spaces[available_state] = gym.spaces.Box(low = 0, high = 1, shape=())
            else:
                ob_spaces[available_state] = gym.spaces.Box(low = -float('inf'), high = float('inf'), shape = ())

        self.action_space = gym.spaces.Box(low = 0, high = 1, shape=())
        self.observation_space = gym.spaces.Dict(ob_spaces)

        self.__crane = TDN_CraneSim_PyIF.CraneSimulator(json.dumps(param_init), json.dumps(state_init))
        self.__num_steps = int(env_params['base_freq']/env_params['evaluation_params']['hz'])
        self.__base_freq = env_params['base_freq']
        self.__zero_action_step_length = env_params['evaluation_params']['wait_sec']*env_params['evaluation_params']['hz']
        self.__max_steps = env_params['max_wait_sec']*env_params['evaluation_params']['hz']
        self.__available_states = env_params['available_states']
        self.__evaluation_states = env_params['evaluation_states']
        self.__evaluation_runtime = env_params['evaluation_runtime']

    def step(self, action):
        # input the action value
        assert isinstance(action, float) and action >= self.action_space.low and action <= self.action_space.high
        self.__crane.set_action_value(action)
        self.__update_action_log(action)

        # step foward
        self.__crane.step(self.__num_steps)

        # get the observation
        state = self.__crane.get_crane_state()
        observation = self.__get_avaiable_observation(state)

        # set the reward
        reward = 0

        # get done flag
        done = self.__get_done_flag()

        # update the log for evaluation
        self.__update_state_results(state)

        return observation, reward, done, {}

    def reset(self):
        self.__crane.reset()
        self.__reset_action_log()
        self.__reset_control_results()

        state = self.__crane.get_crane_state()
        observation = self.__get_avaiable_observation(state)

        return observation

    def render(self):
        pass

    def start(self):
        self.__crane.start()

    def stop(self):
        self.__crane.stop()

    def update_runtime_results(self, runtime):
        for s in self.__evaluation_runtime:
            if s == 'total_steps':
                self.__control_results[s] += 1
            else:
                self.__control_results[s].append(runtime)

    def get_control_results(self):
        results = {}
        for k, v in self.__control_results.items():
            if k != 'senkai_velocity' and k != 'total_steps':
                if k == 'runtime_per_step':
                    results[k] = sorted(v)[-int(0.01*self.__control_results['total_steps']):]
                else:
                    results[k] = v[-self.__zero_action_step_length:]
            else:
                results[k] = v
        return results

    def save_action_log(self, action_log_path):
        with open(action_log_path, 'w') as f:
            json.dump(self.__action_log, f)

    def save_control_results(self, control_results_path):
        results = self.get_control_results()
        with open(control_results_path, 'w') as f:
            json.dump(results, f)

    def __get_done_flag(self):
        min_length_flag = self.__control_results['total_steps'] >= self.__zero_action_step_length
        stop_flag = np.all(np.array(self.__action_log[-self.__zero_action_step_length:]) == 0)
        max_flag = self.__control_results['total_steps'] >= self.__max_steps
        
        return min_length_flag*stop_flag + max_flag

    def __get_avaiable_observation(self, state):
        observation = {s: state[s] for s in self.__available_states}
        
        return observation

    def __reset_action_log(self):
        self.__action_log = []

    def __reset_control_results(self):
        self.__control_results = {s: [] for s in self.__evaluation_states}
        for s in self.__evaluation_runtime:
            if s == 'total_steps':
                self.__control_results[s] = 0
            else:
                self.__control_results[s] = []

    def __update_action_log(self, action):
        self.__action_log.append(action)

    def __update_state_results(self, state):
        for k, v in self.__evaluation_states.items():
            if k == 'senkai_radian':
                self.__control_results[k].append(np.deg2rad(state[v]))
            elif k != 'senkai_velocity':
                self.__control_results[k].append(state[v])
        if len(self.__control_results['senkai_radian']) <= 1:
            velocity = 0
        else:
            velocity = self.__base_freq*(self.__control_results['senkai_radian'][-1] - self.__control_results['senkai_radian'][-2])/self.__num_steps
        self.__control_results['senkai_velocity'].append(velocity)

if __name__ == '__main__':
    # read the parameters
    with open('./configs/env_params.json') as f:
        env_params = json.load(f)
    with open('./configs/sim_params.json') as f:
        sim_params = json.load(f)

    # instanciate the simulator
    crane_env = CraneEnv(env_params, sim_params)

    # sample action and state
    print(crane_env.action_space.sample())
    print(crane_env.observation_space.sample())
