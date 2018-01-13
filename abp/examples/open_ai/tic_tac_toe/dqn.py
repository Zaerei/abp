import time

import gym
import numpy as np
import tensorflow as tf

from abp import DQNAdaptive
from abp.utils import clear_summary_path

def run_task(evaluation_config, network_config, reinforce_config):
    env = gym.make(evaluation_config.env)
    state = env.reset()
    max_episode_steps = env._max_episode_steps

    agent = DQNAdaptive(name = "TicTacToe",
                        choices = range(9),
                        network_config = network_config,
                        reinforce_config = reinforce_config)

    training_summaries_path = evaluation_config.summaries_path + "/train"
    clear_summary_path(training_summaries_path)
    train_summary_writer = tf.summary.FileWriter(training_summaries_path)

    test_summaries_path = evaluation_config.summaries_path + "/test"
    clear_summary_path(test_summaries_path)
    test_summary_writer = tf.summary.FileWriter(test_summaries_path)


    for episode in range(evaluation_config.training_episodes):
        state = env.reset()
        total_reward = 0
        episode_summary = tf.Summary()

        for steps in range(max_episode_steps):
            action, _ = agent.predict(state)

            state, reward, done, info = env.step(action)

            total_reward += reward

            reshaped_board = np.reshape(info['board'], (3,3))

            sum_rows = np.sum(reshaped_board, axis = 1)
            sum_cols = np.sum(reshaped_board, axis = 0)
            sum_diagonal = np.trace(reshaped_board)
            sum_rev_diagonal = np.trace(np.flipud(reshaped_board))

            reward_type = 0

            for row in range(3):
                if sum_rows[row] == 3:
                    agent.reward(10)
                elif sum_rows[row] == -3:
                    agent.reward(-10)

            reward_type = 3

            for col in range(3):
                if sum_cols[col] == 3:
                    agent.reward(10)
                elif sum_cols[col] == -3:
                    agent.reward(-10)

            if sum_diagonal == 3:
                agent.reward(10)
            elif sum_diagonal == -3:
                agent.reward(-10)

            if sum_rev_diagonal == 3:
                agent.reward(10)
            elif sum_diagonal == -3:
                agent.reward(-10)

            if info['illegal_move']:
                agent.reward(-10)
            else:
                agent.reward(1)

            if done:
                agent.end_episode(state)
                episode_summary.value.add(tag = "Episode Reward", simple_value = total_reward)
                train_summary_writer.add_summary(episode_summary, episode + 1)
                break

    train_summary_writer.flush()
    agent.disable_learning()

    # Test Episodes
    for episode in range(evaluation_config.test_episodes):
        state = env.reset()
        total_reward = 0
        episode_summary = tf.Summary()
        for steps in range(max_episode_steps):
            action, q_values = agent.predict(state)

            if evaluation_config.render:
                env.render()
                time.sleep(10)

            state, reward, done, info = env.step(action)
            total_reward += reward

            if done:
                episode_summary.value.add(tag = "Episode Reward", simple_value = total_reward)
                test_summary_writer.add_summary(episode_summary, episode + 1)
                break

    test_summary_writer.flush()
    env.close()