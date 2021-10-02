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
        """
        args:
          params (data type: dict)
            - 'senkai_target_angle'
            - 'weight_t'
            - 'wire_ratio'
            - 'init_kifuku_deg'
            - 'init_yure_senkai_m'
            - 'init_yure_kifuku_m'
            - 'param_randomize_seed'
        """
        self.params = params

    def policy(self, observation):
        """
        args:
          observation (data type: dict):
            - 'step'
            - 'turning_lever_value'
            - 'turning_encoder_angle_deg'
            - 'turning_encoder_acquisition_time'
            - 'working_radius_m'
            - 'actual_load_t'
            - 'main_wire_length_m'
            - 'boom_top_x_m'
            - 'boom_top_y_m'
            - 'boom_top_z_m'
            - 'boom_top_status'
            - 'left_turning_pressure_mpa'
            - 'right_turning_pressure_mpa'
            - 'tawami_diff_deg'
            - 'hook_x_m'
            - 'hook_y_m'
            - 'hook_z_m'
            - 'hook_status'
            - 'hook_diff_c_m'
            - 'hook_diff_r_m'
        available observation

        returns:
          next_lever_value(data type: float, 0 <= and <= 1)
        """
        if observation['turning_encoder_angle_deg'] < self.params['senkai_target_angle']:
            next_lever_value = min(max(observation['turning_lever_value'] + 0.01, self.action_range[0]), self.action_range[1])
        else:
            next_lever_value = 0.0

        return next_lever_value


if __name__ == '__main__':
    import json

    # read the parameters
    with open('./configs/external_params.json') as f:
        params = json.load(f)

    # set the model path
    model_path = './model'
    
    # instanciate the agent
    agent = Agent.get_model(model_path)
    print(agent.model, agent.action_range)

    # set the external parameters
    agent.set_params(params)
    print(agent.params)
