"""Implementation of RiverSwim environment."""

from typing import Any, Dict, Tuple

import gymnasium as gym
import numpy as np
from gymnasium.utils import seeding


class RiverSwimEnv(gym.Env):
    """Minimal RiverSwim environment.

    This environment typically has 6 states and 2 actions (0 or 1).
    The agent starts at the leftmost state (0) and can attempt
    to swim left or right. The rightmost state (n_states-1) has
    a higher reward.
    """

    metadata = {"render_modes": ["ansi"], "render_fps": 1}

    def __init__(
        self,
        n_states: int = 6,
        max_reward: int | float = 10_000,
        intermediate_reward: int | float = 5,
        commom_reward: int | float = 0,
        p_right: float = 0.3,
        p_left: float = 0.1,
        render_mode: str | None = None,
    ) -> None:
        """Initialize the RiverSwim environment.

        Args:
            n_states (int, optional): Number of states in the environment. Defaults to 6.
            max_reward (int | float, optional): Reward to be given at the rightmost state. Defaults to 10_000.
            intermediate_reward (int | float, optional): Reward to be given at the leftmost state. Defaults to 5.
            commom_reward (int | float, optional): Reward to be given throughout the states that are not the main goal or subgoal. Defaults to 0.
            p_right (float, optional): Chance of successfully moving right. Defaults to 0.3.
            p_left (float, optional): Chance of trying to move right and going to the left instead, carried by the current. Defaults to 0.1.
            render_mode (str | None, optional): Mode for rendering.
        """
        self.n_states = n_states
        self.n_actions = 2
        self.current_state: int = self.np_random.choice(
            [0, 1]
        )  # starts at either state 0 or 1, with 50% chance.

        self.action_space = gym.spaces.Discrete(self.n_actions)
        self.observation_space = gym.spaces.Discrete(n_states)

        self.p_right = p_right
        self.p_left = p_left
        self.p_stay = 1 - p_left - p_right

        self.render_mode = render_mode

        self.max_reward = max_reward
        self.intermediate_reward = intermediate_reward
        self.commom_reward = commom_reward

        self.transition = self._get_transition()

    def _get_transition(self) -> np.ndarray:
        """Returns the transition matrix for the environment.

        Returns:
            np.ndarray: transition matrix mapping (state, action, next state).
        """
        transition_matrix: np.ndarray = np.zeros(
            shape=(self.n_states, self.n_actions, self.n_states), dtype=np.float32
        )

        for i in range(self.n_states):
            if i > 0:
                transition_matrix[i, 0, i - 1] = 1.0
                transition_matrix[i, 1, i - 1] = self.p_left
                transition_matrix[i, 1, i] = self.p_stay
            else:
                transition_matrix[i, 0, i] = 1.0
                transition_matrix[i, 1, i] = self.p_stay + self.p_left

            if i < self.n_states - 1:
                transition_matrix[i, 1, i + 1] = self.p_right
            else:
                transition_matrix[i, 1, i] = self.p_right
                transition_matrix[i, 1, i - 1] = 1 - self.p_right

        assert all(transition_matrix[:, 0, :].sum(axis=-1) == 1.0)
        assert all(transition_matrix[:, 1, :].sum(axis=-1) == 1.0)

        return transition_matrix

    def reset(
        self, seed: int | None = None, options=None
    ) -> Tuple[int, Dict[str, Any]]:
        """Reset the environment to the initial state.

        Args:
            seed (int | None, optional): Seed for random number generator.
            options (dict, optional): Additional options for reset.

        Returns:
            int: The initial state (0).
        """
        self.np_random, _ = seeding.np_random(seed)
        self.current_state = 0
        info = {}
        return self.current_state, info

    def step(self, action: int) -> Tuple[int, int | float, bool, bool, Dict[str, Any]]:
        """Take an action and progress the environment state.

        Args:
            action (int): The chosen action (0 = swim left, 1 = swim right).

        Raises:
            ValueError: If the action is not 0 or 1.

        Returns:
            tuple[int, float, bool, dict]: A tuple containing the next state,
                the reward, a done flag, and an info dictionary.
        """
        if action not in [0, 1]:
            raise ValueError("Invalid action. Must be 0 or 1.")

        probabilities = self.transition[self.current_state, action, :]
        next_state = self.np_random.choice(self.n_states, p=probabilities)

        reward = self.commom_reward
        if self.current_state == next_state:
            if (next_state == 0) and (action == 0):
                reward = self.intermediate_reward
            elif (next_state == self.n_states - 1) and (action == 1):
                reward = self.max_reward

        self.current_state = next_state
        terminal = False
        truncated = False
        info = {}
        return next_state, reward, terminal, truncated, info

    def render(self) -> None:
        """Render the current environment state.

        Prints a simple textual representation if render_mode is "human".
        """
        if self.render_mode == "ansi":
            representation = ""
            for i in range(self.n_states):
                if i == self.current_state:
                    representation += "[X]"
                else:
                    representation += "[ ]"
                if i < self.n_states - 1:
                    representation += " - "
            print(f"RiverSwim State: {representation}")


if __name__ == "__main__":
    """
    Temporary environment tester function.
    """
    env = RiverSwimEnv(render_mode="ansi")

    obs, info = env.reset()

    print("\nAction left:\n", env.transition[:, 0, :])
    print("\nAction right:\n", env.transition[:, 1, :], "\n\n")

    env.render()

    terminal = False
    step = 0
    while not terminal:
        print(f"\nStep {step}")
        env.render()
        action = int(input("Please input an action\n"))
        obs, reward, terminal, truncated, info = env.step(action)
        print(f"Reward: {reward}\n")

        step += 1

    exit()
