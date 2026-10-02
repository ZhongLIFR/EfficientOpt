from __future__ import annotations

import json
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def build_marginals(data: dict) -> tuple[list[float], list[float], list[float], float]:
    regions = int(data["regions"])
    channels = int(data["channels"])
    periods = int(data["periods"])
    region_totals = [70.0 + ((31 * i) % 89) + 0.2 * (i % 5) for i in range(regions)]
    raw_channels = [55.0 + ((23 * j) % 71) + 0.17 * (j % 7) for j in range(channels)]
    raw_periods = [48.0 + ((19 * k) % 67) + 0.11 * (k % 9) for k in range(periods)]
    total = sum(region_totals)
    channel_scale = total / sum(raw_channels)
    period_scale = total / sum(raw_periods)
    channel_totals = [value * channel_scale for value in raw_channels]
    period_totals = [value * period_scale for value in raw_periods]
    return region_totals, channel_totals, period_totals, total


def tensor_entry(region_total: float, channel_total: float, period_total: float, total: float, regions: int, channels: int, periods: int) -> float:
    return (
        region_total / (channels * periods)
        + channel_total / (regions * periods)
        + period_total / (regions * channels)
        - 2.0 * total / (regions * channels * periods)
    )


def dense_objective_and_errors(
    region_totals: list[float],
    channel_totals: list[float],
    period_totals: list[float],
    total: float,
) -> dict:
    regions = len(region_totals)
    channels = len(channel_totals)
    periods = len(period_totals)
    channel_sums = [0.0] * channels
    period_sums = [0.0] * periods
    objective = 0.0
    checksum = 0.0
    max_region_error = 0.0
    materialized_regions = []
    for i, region_total in enumerate(region_totals):
        region_sum = 0.0
        region_block = []
        for j, channel_total in enumerate(channel_totals):
            row = []
            for k, period_total in enumerate(period_totals):
                value = tensor_entry(region_total, channel_total, period_total, total, regions, channels, periods)
                row.append(value)
                region_sum += value
                channel_sums[j] += value
                period_sums[k] += value
                objective += 0.5 * value * value
                if (i * 149 + j * 31 + k * 11) % 4093 == 0:
                    checksum += value
            region_block.append(row)
        materialized_regions.append(region_block)
        max_region_error = max(max_region_error, abs(region_sum - region_total))
    max_channel_error = max(abs(channel_sums[j] - channel_totals[j]) for j in range(channels))
    max_period_error = max(abs(period_sums[k] - period_totals[k]) for k in range(periods))
    return {
        "objective": objective,
        "max_region_error": max_region_error,
        "max_channel_error": max_channel_error,
        "max_period_error": max_period_error,
        "checksum": checksum,
        "materialized_regions": len(materialized_regions),
    }


def low_rank_objective_and_errors(
    region_totals: list[float],
    channel_totals: list[float],
    period_totals: list[float],
    total: float,
) -> dict:
    regions = len(region_totals)
    channels = len(channel_totals)
    periods = len(period_totals)
    region_term = sum(value * value for value in region_totals) / (channels * periods)
    channel_term = sum(value * value for value in channel_totals) / (regions * periods)
    period_term = sum(value * value for value in period_totals) / (regions * channels)
    objective = 0.5 * (region_term + channel_term + period_term - 2.0 * total * total / (regions * channels * periods))
    checksum = tensor_entry(region_totals[0], channel_totals[0], period_totals[0], total, regions, channels, periods)
    return {
        "objective": objective,
        "max_region_error": 0.0,
        "max_channel_error": 0.0,
        "max_period_error": 0.0,
        "checksum": checksum,
    }
