import os
import torch as T
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


class CriticNetwork(nn.Module):
    def __init__(
        self, beta, input_dims, fc1=400, fc2=300, name="critic", checkpoint_dir="models"
    ):
        super(CriticNetwork, self).__init__()
        self.beta = beta
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_file = os.path.join(self.checkpoint_dir, name + "_maddpg")
        # Easier to incoperate number of actions, number of agents into input dimensions
        self.fc1 = nn.Linear(input_dims, fc1)
        self.fc2 = nn.Linear(fc1, fc2)
        self.q = nn.Linear(fc2, 1)

        self.optimizer = optim.Adam(self.parameters(), lr=self.beta)
        self.device = T.device("cuda:0" if T.cuda.is_available() else "cpu")
        self.to(self.device)

    def forward(self, state, action):
        state_action_value = F.relu(self.fc1(T.cat([state, action], dim=1)))
        state_action_value = F.relu(self.fc2(state_action_value))
        return self.q(state_action_value)

    def save_checkpoint(self):
        print("... saving checkpoint ...")
        T.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        print("... loading checkpoint ...")
        self.load_state_dict(T.load(self.checkpoint_file))


class ActorNetwork(nn.Module):
    def __init__(
        self,
        alpha,
        input_dims,
        n_actions,
        max_action=1,
        fc1=300,
        fc2=400,
        name="actor",
        checkpoint_dir="models",
    ):
        super(ActorNetwork, self).__init__()
        self.alpha = alpha
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_file = os.path.join(self.checkpoint_dir, name + "maddpg")

        self.fc1 = nn.Linear(input_dims, fc1)
        self.fc2 = nn.Linear(fc1, fc2)
        self.mu = nn.Linear(fc2, n_actions)

        self.max_action = max_action

        self.optimizer = optim.Adam(self.parameters(), lr=self.alpha)

        self.device = T.device("cuda:0" if T.cuda.is_available() else "cpu")
        self.to(self.device)

    def forward(self, state):
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        x = T.tanh(self.mu(x))
        return self.max_action * x

    def save_checkpoint(self):
        print("... saving checkpoint ...")
        T.save(self.state_dict(), self.checkpoint_file)

    def load_checkpoint(self):
        print("... loading checkpoint ...")
        self.load_state_dict(T.load(self.checkpoint_file))