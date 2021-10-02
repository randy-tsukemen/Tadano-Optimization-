import env_user
import agent
import json
import time

def play(env, agent, output_path):
    # get the initial observation
    observation = env.reset()
    
    # start the simulator
    env.start()
    done = False
    while not done:
        # time the control
        time_start = time.perf_counter()
        action = agent.policy(observation)
        runtime = time.perf_counter() - time_start
        env.update_runtime_results(runtime)
        
        # step foward
        observation, reward, done, info = env.step(action)
        print(observation['step'], observation['turning_lever_value'], done)

    # save the control results
    env.save_control_results(output_path)

    # stop the simulator
    env.stop()

def main():
    # read the parameters
    with open('./configs/env_params.json') as f:
        env_params = json.load(f)
    with open('./configs/sim_params.json') as f:
        sim_params = json.load(f)
    with open('./configs/external_params.json') as f:
        external_params = json.load(f)
    external_params.update(sim_params['state_init'])
    
    # instanciate the simulator
    crane_env = env_user.CraneEnv(env_params, sim_params)
    
    # instanciate the agent
    crane_agent = agent.Agent.get_model('./model')
    crane_agent.set_params(external_params)
    
    # run the simulator with agent
    output_path = './output/control_results.json'
    play(crane_env, crane_agent, output_path)

if __name__ == '__main__':
    main()
