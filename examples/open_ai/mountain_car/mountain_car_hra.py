import gym
from abp.hra.adaptive import Adaptive
from math import sqrt

env = gym.make("MountainCar-v0")

state = env.reset()

#TODO  Incomplete implementation


agent = Adaptive(env.action_space.n, len(state), "Mountain Car", decay_steps = 1000)

#Training Episodes
for epoch in range(300):
    state = env.reset()
    prev_position = None
    prev_velocity = None
    previous_action  = None
    for t in range(300):
        action = agent.predict(state)
        state, reward, done, info = env.step(action)
        position, velocity = state
        agent.reward(reward)

        if prev_velocity and prev_position:
            change_velocity = sqrt( (velocity ** 2) - (prev_velocity ** 2))
            change_position = position - prev_position


        agent.reward(position)

        if action == 1:
            agent.reward(-1)

        prev_position, prev_velocity, previous_action = position, velocity, action

        if done:
            agent.end_episode(state)
            break

agent.disable_learning()

#Testing Episodes
for epoch in range(30):
    state = env.reset()
    prev_position = None
    for t in range(300):
        env.render()
        action = agent.predict(state)
        state, reward, done, info = env.step(action)
        position, velocity = state
        agent.reward(reward)

        agent.reward(position)

        if action == 1:
            agent.reward(-1)

        prev_position = position

        if done:
            agent.end_episode(state)
            break



env.close()