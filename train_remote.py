import os
from pathlib import Path

import torch

from src.Game.AI.selfplay_trainer import SelfPlayTrainer
from src.Game.Board.chessboard import WithoutTimerChess


def as_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def as_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def main() -> None:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    checkpoint_dir = Path(os.getenv("CHECKPOINT_DIR", "/app/models"))
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    trainer = SelfPlayTrainer(
        device=device,
        lr=as_float("LEARNING_RATE", 1e-3),
        search_depth=as_int("SEARCH_DEPTH", 1),
        quiescence_limit=as_int("QUIESCENCE_LIMIT", 0),
        max_plies_per_game=as_int("MAX_PLIES_PER_GAME", 60),
        epsilon=as_float("EPSILON", 0.15),
        temperature=as_float("TEMPERATURE", 0.90),
    )

    resume = os.getenv("RESUME_CHECKPOINT", "").strip()
    if resume:
        trainer.load_checkpoint(resume)
        print(f"Loaded checkpoint: {resume}", flush=True)

    print(f"Training device: {device}", flush=True)
    if device == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}", flush=True)

    history = trainer.fit(
        WithoutTimerChess,
        generations=as_int("GENERATIONS", 5),
        games_per_generation=as_int("GAMES_PER_GENERATION", 8),
        train_batches=as_int("TRAIN_BATCHES", 20),
        batch_size=as_int("BATCH_SIZE", 128),
        checkpoint_dir=checkpoint_dir,
    )

    latest = checkpoint_dir / "chess_value_net_latest.pt"
    if latest.exists():
        print(f"Latest model: {latest}", flush=True)
    print(f"History: {history}", flush=True)


if __name__ == "__main__":
    main()
