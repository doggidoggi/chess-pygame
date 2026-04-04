from __future__ import annotations

import math
import random
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Optional

import torch
import torch.nn.functional as F
from torch import nn, optim

from src.Game.AI.chess_encoder import BoardEncoder
from src.Game.AI.self_learning_ai import (
    ChessValueNet,
    NeuralEvaluator,
    SearchConfig,
    apply_ai_move,
    negamax,
    order_moves,
)


@dataclass(slots=True)
class TrainingExample:
    state: torch.Tensor
    target_value: float


class ReplayBuffer:
    def __init__(self, capacity: int = 50_000) -> None:
        self.capacity = capacity
        self._items: Deque[TrainingExample] = deque(maxlen=capacity)

    def add(self, item: TrainingExample) -> None:
        self._items.append(item)

    def extend(self, items: list[TrainingExample]) -> None:
        self._items.extend(items)

    def sample(self, batch_size: int) -> list[TrainingExample]:
        batch_size = min(batch_size, len(self._items))
        return random.sample(list(self._items), batch_size)

    def __len__(self) -> int:
        return len(self._items)


class SelfPlayTrainer:
    """
    Минимальный self-play trainer под текущий движок.

    Подход:
    - сеть оценивает позиции в диапазоне [-1, 1]
    - агент играет сам с собой
    - для каждой позиции сохраняется итог партии с точки зрения side-to-move
    - после серии партий сеть дообучается по MSE
    """

    def __init__(
        self,
        model: Optional[nn.Module] = None,
        *,
        encoder: Optional[BoardEncoder] = None,
        device: str | torch.device = "cpu",
        lr: float = 1e-3,
        replay_capacity: int = 50_000,
        search_depth: int = 2,
        quiescence_limit: int = 4,
        max_plies_per_game: int = 200,
        epsilon: float = 0.15,
        temperature: float = 0.90,
    ) -> None:
        self.device = torch.device(device)
        self.model = (model or ChessValueNet()).to(self.device)
        self.encoder = encoder or BoardEncoder()
        self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
        self.replay_buffer = ReplayBuffer(capacity=replay_capacity)
        self.search_config = SearchConfig(depth=search_depth, quiescence_limit=quiescence_limit)
        self.max_plies_per_game = max_plies_per_game
        self.epsilon = float(epsilon)
        self.temperature = float(temperature)

    def build_evaluator(self) -> NeuralEvaluator:
        return NeuralEvaluator(self.model, self.encoder, device=self.device)

    def play_self_play_game(self, board_factory) -> tuple[list[TrainingExample], int]:
        board = board_factory()
        history: list[tuple[torch.Tensor, int]] = []
        evaluator = self.build_evaluator()

        for _ in range(self.max_plies_per_game):
            legal_moves = board.getValidMoves()
            if not legal_moves:
                break

            side_multiplier = 1 if board.whiteMove else -1
            history.append((self.encoder.encode(board).cpu(), side_multiplier))

            move = self._sample_selfplay_move(board, evaluator)
            if move is None:
                break
            apply_ai_move(board, move)

        result = self._resolve_game_result(board, max_plies_reached=len(history) >= self.max_plies_per_game)

        examples = [
            TrainingExample(state=state, target_value=float(result * side_multiplier))
            for state, side_multiplier in history
        ]
        return examples, result

    def generate_self_play_data(self, board_factory, games: int = 10) -> list[TrainingExample]:
        collected: list[TrainingExample] = []
        for _ in range(games):
            examples, _ = self.play_self_play_game(board_factory)
            collected.extend(examples)
        self.replay_buffer.extend(collected)
        return collected

    def train_epoch(self, batch_size: int = 256, batches: int = 100) -> float:
        if len(self.replay_buffer) == 0:
            return 0.0

        self.model.train()
        total_loss = 0.0
        actual_batches = 0

        for _ in range(batches):
            batch = self.replay_buffer.sample(batch_size)
            if not batch:
                continue

            states = torch.stack([item.state for item in batch]).to(self.device)
            targets = torch.tensor(
                [[item.target_value] for item in batch],
                dtype=torch.float32,
                device=self.device,
            )

            preds = self.model(states)
            loss = F.mse_loss(preds, targets)

            self.optimizer.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_loss += float(loss.item())
            actual_batches += 1

        self.model.eval()
        if actual_batches == 0:
            return 0.0
        return total_loss / actual_batches

    def fit(
        self,
        board_factory,
        *,
        generations: int = 20,
        games_per_generation: int = 20,
        train_batches: int = 100,
        batch_size: int = 256,
        checkpoint_dir: str | Path | None = None,
    ) -> list[dict[str, float]]:
        history: list[dict[str, float]] = []
        checkpoint_path = Path(checkpoint_dir) if checkpoint_dir is not None else None
        if checkpoint_path is not None:
            checkpoint_path.mkdir(parents=True, exist_ok=True)

        for generation in range(1, generations + 1):
            examples = self.generate_self_play_data(board_factory, games=games_per_generation)
            loss = self.train_epoch(batch_size=batch_size, batches=train_batches)

            stats = {
                "generation": float(generation),
                "examples": float(len(examples)),
                "buffer_size": float(len(self.replay_buffer)),
                "loss": float(loss),
            }
            history.append(stats)

            if checkpoint_path is not None:
                checkpoint_file = checkpoint_path / f"generation_{generation:03d}.pt"
                self.save_checkpoint(checkpoint_file)
                self.save_checkpoint(checkpoint_path / "generation_latest.pt")
                self.save_checkpoint(checkpoint_path / "chess_value_net_latest.pt")

        return history

    def save_checkpoint(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "search_depth": self.search_config.depth,
                "quiescence_limit": self.search_config.quiescence_limit,
                "max_plies_per_game": self.max_plies_per_game,
                "epsilon": self.epsilon,
                "temperature": self.temperature,
            },
            path,
        )

    def load_checkpoint(self, path: str | Path) -> None:
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        self.search_config.depth = int(checkpoint.get("search_depth", self.search_config.depth))
        self.search_config.quiescence_limit = int(
            checkpoint.get("quiescence_limit", self.search_config.quiescence_limit)
        )
        self.max_plies_per_game = int(checkpoint.get("max_plies_per_game", self.max_plies_per_game))
        self.epsilon = float(checkpoint.get("epsilon", self.epsilon))
        self.temperature = float(checkpoint.get("temperature", self.temperature))
        self.model.eval()

    def _sample_selfplay_move(self, board, evaluator) -> object | None:
        legal_moves = board.getValidMoves()
        if not legal_moves:
            return None
        if len(legal_moves) == 1:
            return legal_moves[0]
        if random.random() < self.epsilon:
            return random.choice(legal_moves)

        ordered_moves = order_moves(legal_moves)
        color_multiplier = 1 if board.whiteMove else -1
        move_scores: list[float] = []

        for move in ordered_moves:
            apply_ai_move(board, move)
            score = -negamax(
                board,
                self.search_config.depth - 1,
                -math.inf,
                math.inf,
                -color_multiplier,
                evaluator,
                ply=1,
                search_config=self.search_config,
            )
            board.undoMove()
            move_scores.append(score)

        probabilities = self._softmax_scores(move_scores, self.temperature)
        selected_index = random.choices(range(len(ordered_moves)), weights=probabilities, k=1)[0]
        return ordered_moves[selected_index]

    @staticmethod
    def _softmax_scores(scores: list[float], temperature: float) -> list[float]:
        temperature = max(temperature, 1e-3)
        normalized = [score / temperature for score in scores]
        max_score = max(normalized)
        exps = [math.exp(score - max_score) for score in normalized]
        total = sum(exps)
        if total <= 0:
            return [1.0 / len(scores)] * len(scores)
        return [value / total for value in exps]

    @staticmethod
    def _resolve_game_result(board, *, max_plies_reached: bool) -> int:
        if max_plies_reached:
            return 0

        legal_moves = board.getValidMoves()
        if legal_moves:
            return 0

        if board.inCheck():
            return -1 if board.whiteMove else 1
        return 0
