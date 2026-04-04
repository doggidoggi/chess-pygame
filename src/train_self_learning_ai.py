from __future__ import annotations

import argparse
from pathlib import Path

import torch

from src.constants import PROJECT_DIR
from src.Game.AI.selfplay_trainer import SelfPlayTrainer
from src.Game.Board.chessboard import WithoutTimerChess


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Train self-learning chess AI on the current pygame engine.')
    parser.add_argument('--generations', type=int, default=20)
    parser.add_argument('--games-per-generation', type=int, default=20)
    parser.add_argument('--train-batches', type=int, default=80)
    parser.add_argument('--batch-size', type=int, default=256)
    parser.add_argument('--search-depth', type=int, default=2)
    parser.add_argument('--quiescence-limit', type=int, default=4)
    parser.add_argument('--epsilon', type=float, default=0.15)
    parser.add_argument('--temperature', type=float, default=0.90)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--checkpoint-dir', type=Path, default=PROJECT_DIR / 'models')
    parser.add_argument('--resume', type=Path, default=None)
    return parser


def board_factory() -> WithoutTimerChess:
    return WithoutTimerChess()


def main() -> None:
    args = build_parser().parse_args()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    trainer = SelfPlayTrainer(
        device=device,
        lr=args.lr,
        search_depth=args.search_depth,
        quiescence_limit=args.quiescence_limit,
        epsilon=args.epsilon,
        temperature=args.temperature,
    )

    if args.resume is not None and args.resume.is_file():
        trainer.load_checkpoint(args.resume)
        print(f'Loaded checkpoint: {args.resume}')

    history = trainer.fit(
        board_factory,
        generations=args.generations,
        games_per_generation=args.games_per_generation,
        train_batches=args.train_batches,
        batch_size=args.batch_size,
        checkpoint_dir=args.checkpoint_dir,
    )

    latest = args.checkpoint_dir / 'chess_value_net_latest.pt'
    print(f'Saved latest checkpoint to: {latest}')
    for row in history:
        print(
            f"generation={int(row['generation'])} "
            f"examples={int(row['examples'])} "
            f"buffer={int(row['buffer_size'])} "
            f"loss={row['loss']:.6f}"
        )


if __name__ == '__main__':
    main()
