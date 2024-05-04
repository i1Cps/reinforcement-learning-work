import numpy as np
from typing import List, Tuple


class MultiAgentReplayBuffer:
    def __init__(
        self,
        max_size: int,
        critic_dims: int,
        actor_dims: List[int],
        n_actions: List[int],
        n_agents: int,
        batch_size: int,
    ):
        self.mem_size = max_size
        self.mem_counter = 0
        self.n_agents = n_agents
        self.actor_dims = actor_dims
        self.batch_size = batch_size
        self.n_actions = n_actions

        self.state_memory = np.zeros((self.mem_size, critic_dims))
        self.next_state_memory = np.zeros((self.mem_size, critic_dims))
        self.reward_memory = np.zeros((self.mem_size, n_agents))
        self.terminal_memory = np.zeros((self.mem_size, n_agents), dtype=bool)

        self.init_actor_memory()

    def init_actor_memory(self):
        self.actor_state_memory = []
        self.actor_next_state_memory = []
        self.actor_action_memory = []

        for i in range(self.n_agents):
            self.actor_state_memory.append(
                np.zeros((self.mem_size, self.actor_dims[i]))
            )
            self.actor_next_state_memory.append(
                np.zeros((self.mem_size, self.actor_dims[i]))
            )
            self.actor_action_memory.append(
                np.zeros((self.mem_size, self.n_actions[i]))
            )

    def store_transition(
        self,
        raw_obs: List[np.ndarray],
        state: np.ndarray,
        action: List[np.ndarray],
        reward: List,
        next_raw_obs: List[np.ndarray],
        next_state: np.ndarray,
        done: List[bool],
    ):
        index = self.mem_counter % self.mem_size
        for agent_idx in range(self.n_agents):
            self.actor_state_memory[agent_idx][index] = raw_obs[agent_idx]
            self.actor_next_state_memory[agent_idx][index] = next_raw_obs[agent_idx]
            self.actor_action_memory[agent_idx][index] = action[agent_idx]

        self.state_memory[index] = state
        self.next_state_memory[index] = next_state
        self.reward_memory[index] = reward
        self.terminal_memory[index] = done
        self.mem_counter += 1

    def sample_buffer(
        self,
    ) -> Tuple[
        List[np.ndarray],
        np.ndarray,
        List[np.ndarray],
        np.ndarray,
        List[np.ndarray],
        np.ndarray,
        np.ndarray,
    ]:
        max_mem = min(self.mem_counter, self.mem_size)

        batch = np.random.choice(max_mem, self.batch_size, replace=False)

        states = self.state_memory[batch]
        next_states = self.next_state_memory[batch]
        rewards = self.reward_memory[batch]
        terminal = self.terminal_memory[batch]

        actor_states = []
        actor_next_states = []
        actions = []

        for agent_idx in range(self.n_agents):
            actor_states.append(self.actor_state_memory[agent_idx][batch])
            actor_next_states.append(self.actor_next_state_memory[agent_idx][batch])
            actions.append(self.actor_action_memory[agent_idx][batch])

        return (
            actor_states,
            states,
            actions,
            rewards,
            actor_next_states,
            next_states,
            terminal,
        )

    def ready(self) -> bool:
        return self.mem_counter >= self.batch_size
