import numpy as np
from dqn.utils import plot_learning_curve, make_env
from dqn.dqn import DQN

if __name__ == "__main__":
    env = make_env("PongNoFrameskip-v4")

    # Negative scoring game,
    best_score = -np.inf
    load_checkpoint = False
    n_games = 500
    dqn = DQN(
        n_actions=env.action_space.n,
        input_dims=(env.observation_space.shape),
        mem_size=50000,
        batch_size=32,
        gamma=0.99,
        learning_rate=0.0001,
        epsilon=1,
        eps_dec=1e-5,
        eps_min=0.1,
        replace=1000,
        env_name="Pong-v4",
    )

    if load_checkpoint:
        dqn.load_models()

    figure_file = "dqn/plots/" + "__" + str(n_games) + "_games" + ".png"

    n_steps = 0
    scores, steps_array, eps_history = [], [], []

    for i in range(n_games):
        score = 0
        observation = env.reset()
        terminal = False
        truncated = False

        while not (terminal or truncated):
            action = dqn.choose_action(observation)
            observation_, reward, terminal, truncated, info = env.step(action)
            score += reward

            if not load_checkpoint:
                dqn.store_transition(
                    observation, action, reward, observation_, terminal, truncated
                )

                dqn.learn()
            obervation = observation_
            n_steps += 1

        scores.append(score)
        steps_array.append(n_steps)
        avg_score = np.mean(scores[-100:])
        print(
            "episode: ",
            i,
            "score: ",
            score,
            " average score %.1f" % avg_score,
            "best score %.2f" % best_score,
            "epsilon %.2f" % dqn.epsilon,
            "steps",
            n_steps,
        )

        if avg_score > best_score:
            if not load_checkpoint:
                dqn.save_models()
            best_score = avg_score

        eps_history.append(dqn.epsilon)

    plot_learning_curve(steps_array, scores, eps_history, figure_file)
