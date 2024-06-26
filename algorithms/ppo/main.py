import numpy as np
from pathlib import Path
import torch
from agent import Agent
import gymnasium as gym
from memory import PPOMemory
from utils import plot_learning_curve


# Convert action range from [0,1] to [-max action, max action]
def action_adapter(a, max_a):
    return 2 * (a - 0.5) * max_a


# Drastically increases performance
def clip_reward(x):
    if x < -1:
        return -1
    elif x > 1:
        return 1
    else:
        return x


if __name__ == "__main__":
    env_id = "BipedalWalker-v3"
    seed = 0
    torch.manual_seed(seed)
    np.random.seed(seed)
    env = gym.make(env_id)
    load_model = False

    T = 2048
    num_mini_batch = 32
    n_epochs = 15
    max_steps = 1_000_000
    max_action = env.action_space.high[0]
    learning_rate = 3e-4

    agent = Agent(
        actor_dims=env.observation_space.shape[0],
        critic_dims=env.observation_space.shape[0],
        n_actions=env.action_space.shape[0],
        alpha=learning_rate,
        beta=learning_rate,
        entropy_coefficient=1e-3,
        gae_lambda=0.95,
        policy_clip=0.2,
        n_epochs=n_epochs,
        gamma=0.99,
        actor_fc1=128,
        actor_fc2=128,
        critic_fc1=128,
        critic_fc2=128,
    )

    memory = PPOMemory(
        T=T,
        input_dims=env.observation_space.shape[0],
        num_mini_batch=num_mini_batch,
        n_actions=env.action_space.shape[0],
    )

    file_path = (
        "bipedal_walker_"
        + str(learning_rate)
        + "learning_rate_"
        + str(n_epochs)
        + "_epochs_"
        + str(max_steps)
        + "_steps"
    )
    model_file_dir = Path("model_weights") / file_path
    model_file_dir.mkdir(parents=True, exist_ok=True)

    if load_model:
        agent.load(model_file_dir)

    score_history = []
    total_steps = 0
    trajectory_len = 0
    episode = 0
    best_score = -np.Inf

    while total_steps < max_steps:
        # Reset environment and get initial state
        observation, info = env.reset(seed=seed)
        done = False
        score = 0
        while not done:
            action, prob = agent.choose_action(observation)
            # Convert action to correct action space
            adapted_action = action_adapter(action, max_action)
            next_observation, reward, terminated, truncated, info = env.step(
                adapted_action
            )

            done = terminated or truncated
            # Clip reward for drastically better learning
            clipped_reward = clip_reward(reward)
            score += reward

            # Build store memory
            memory.store_memory(
                state=observation,
                action=action,
                reward=clipped_reward,
                next_state=next_observation,
                terminal=done,
                prob=prob,
            )

            total_steps += 1
            trajectory_len += 1

            # Once trajectory has completed start learning sequence
            if trajectory_len % T == 0:
                agent.learn(memory)
                trajectory_len = 0
            observation = next_observation

        score_history.append(score)
        avg_score = np.mean(score_history[-100:])
        if avg_score > best_score:
            best_score = avg_score
            agent.save(model_file_dir)
        print(
            "{} Episode {} total steps {}  avg_score {:.1f}".format(
                env_id, episode, total_steps, avg_score
            )
        )
        episode += 1
    x = [i + 1 for i in range(episode)]
    plot_dir = Path("plots")
    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_file_path = plot_dir / (file_path + ".png")
    plot_learning_curve(x, score_history, plot_file_path)
