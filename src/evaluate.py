import json
import os
import numpy as np


def evaluation_crane(result, params, pattern):
    """
    evaluation for controller
    """
    num_interval = params['num_velocity_interval']
    hz = params['hz']
    senkai_target_distance_threshold = params['senkai_target_distance_threshold']

    flag = 1

    ## validation
    print(' Validation:')
    # angular acceleratioin
    vel = result['senkai_velocity']
    acc = np.array([hz * abs(vel[i + num_interval] - vel[i])/num_interval for i in range(len(vel) - num_interval)])
    r = (acc > params['acceleration_threshold']).sum() < params['max_acceleration_count']
    print('  max angular acceleration: {}[rad/s^2] (threshold: {}[rad/s^2])'.format(acc.max(), params['acceleration_threshold']))
    flag *= r

    # runtime per step
    runtime_per_step_median = np.median(result['runtime_per_step'])
    r = runtime_per_step_median <= params['max_runtime_per_step']
    print('  max runtime per step: {}[s] (threshold: {}[s])'.format(runtime_per_step_median, params['max_runtime_per_step']))
    flag *= r

    # senkai target distance
    senkai_sin = np.abs(np.sin((np.array(result['senkai_radian']) - np.deg2rad(pattern['senkai_target_angle']))/2))
    senkai_dist = 2*(result['working_radius_m']*senkai_sin).mean()
    r = senkai_dist <= senkai_target_distance_threshold
    print('  senkai_distance: {}[m] (threshold: {}[m])'.format(senkai_dist, senkai_target_distance_threshold))
    flag *= r

    ## compute score
    print(' Evaluation:')
    # senkai error
    e = min(senkai_dist, params['senkai_error_upper_bound'])/params['senkai_error_upper_bound']
    print('  senkai error: {} (senkai distance: {}[m])'.format(1 - e, senkai_dist))

    # hook displacement
    hook_displacement = np.sqrt(np.array(result['circular_displacement'])**2 + np.array(result['radial_displacement'])**2).mean()
    d = min(hook_displacement, params['hook_displacement_upper_bound'])/params['hook_displacement_upper_bound']
    print('  hook displacement error: {} (hook displacement: {}[m])'.format(1 - d, hook_displacement))

    # total steps
    diff_lower = params['max_senkai_target_angle_sec_lower_bound'] - params['min_senkai_target_angle_sec_lower_bound']
    diff_upper = params['max_senkai_target_angle_sec_upper_bound'] - params['min_senkai_target_angle_sec_upper_bound']
    diff_angle = params['max_senkai_target_angle'] - params['min_senkai_target_angle']
    a_lower = diff_lower/diff_angle
    a_upper = diff_upper/diff_angle
    diff_target_min = pattern['senkai_target_angle'] - params['min_senkai_target_angle']
    lower_bound = a_lower * diff_target_min + params['min_senkai_target_angle_sec_lower_bound']
    upper_bound = a_upper * diff_target_min + params['min_senkai_target_angle_sec_upper_bound']
    without_wait_time = result['total_steps']/params['hz'] - params['wait_sec']
    total_steps = min(max(without_wait_time, lower_bound), upper_bound)
    s = (total_steps - lower_bound)/(upper_bound - lower_bound)
    print('  total steps: {} (time: {}[s], lower bound: {}[s], upper bound: {}[s])'.format(1 - s, without_wait_time, lower_bound, upper_bound))

    # weight for total steps
    gamma = 1 - params['weight_senkai_error'] - params['weight_hook_displacement_error']

    # final score
    score = 1 - (params['weight_senkai_error']*e + params['weight_hook_displacement_error']*d + gamma*s)

    if flag:
        print('\nValidation OK')
    else:
        print('\nValidation NG')

    return flag, score


if __name__ == '__main__':
    # read parameters
    with open('./configs/evaluation_params.json') as f:
        params = json.load(f)
    with open('./configs/external_params.json') as f:
        external_params = json.load(f)
    print('Parameters for evaluation:')
    for k, v in params.items():
        print(' ', k, v)
    for k, v in external_params.items():
        print(' ', k, v)

    # read the control result
    with open('./output/control_results.json') as f:
        result = json.load(f)
    print('\nCategories for evaluation:')
    for k in result.keys():
        print(' ', k)

    # evaluate the result
    print('\nEvaluation results:')
    flag, score = evaluation_crane(result, params, external_params)
    if flag:
        print('Score: {}'.format(score))
    else:
        print('Score: 0')
