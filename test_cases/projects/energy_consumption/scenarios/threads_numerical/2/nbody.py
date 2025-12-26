import argparse
import concurrent.futures
import math
from typing import Iterable, List, Tuple

from src.client_interface import set_output_filename, set_tag
from test_cases.util import runtime_flavor_suffix


Vector = Tuple[float, float, float]

# Gravitational constant
G_CONSTANT = 6.67430e-11


def chunk_indices(total_items: int, num_workers: int) -> Iterable[Tuple[int, int]]:
    """
    Yield (start, end) index pairs that partition the items across workers.
    """
    items_per_worker = (total_items + num_workers - 1) // num_workers
    for worker_index in range(num_workers):
        start_index = worker_index * items_per_worker
        end_index = min(start_index + items_per_worker, total_items)
        if start_index >= total_items:
            break
        yield start_index, end_index


def seed_positions(num_particles: int) -> List[Vector]:
    """
    Deterministically seed particle positions in a 3D lattice pattern.
    """
    positions: List[Vector] = []
    side = int(round(num_particles ** (1 / 3))) or 1
    scale = 1e3
    for idx in range(num_particles):
        x = ((idx % side) - side / 2) * scale
        y = (((idx // side) % side) - side / 2) * scale
        z = ((idx // (side * side)) - side / 2) * scale
        positions.append((x, y, z))
    return positions


def seed_velocities(num_particles: int) -> List[Vector]:
    """
    Deterministically seed particle velocities with small variations.
    """
    velocities: List[Vector] = []
    for idx in range(num_particles):
        velocities.append((0.0, 0.0, 0.0 if idx % 2 == 0 else 1e-3))
    return velocities


def compute_step_for_slice(
    start_index: int,
    end_index: int,
    positions: List[Vector],
    velocities: List[Vector],
    delta_t: float,
    softening: float,
) -> Tuple[List[Vector], List[Vector]]:
    """
    Compute updated positions and velocities for a slice of particles.
    """
    num_particles = len(positions)
    updated_positions: List[Vector] = []
    updated_velocities: List[Vector] = []

    for particle_index in range(start_index, end_index):
        pos_x, pos_y, pos_z = positions[particle_index]
        vel_x, vel_y, vel_z = velocities[particle_index]

        acc_x = acc_y = acc_z = 0.0
        for other_index in range(num_particles):
            if particle_index == other_index:
                continue
            other_x, other_y, other_z = positions[other_index]
            delta_x = other_x - pos_x
            delta_y = other_y - pos_y
            delta_z = other_z - pos_z
            distance_sq = delta_x * delta_x + delta_y * delta_y + delta_z * delta_z + softening
            inv_distance = 1.0 / math.sqrt(distance_sq)
            inv_distance_cubed = inv_distance * inv_distance * inv_distance
            factor = G_CONSTANT * inv_distance_cubed
            acc_x += factor * delta_x
            acc_y += factor * delta_y
            acc_z += factor * delta_z

        # Update velocity and position
        new_vel_x = vel_x + acc_x * delta_t
        new_vel_y = vel_y + acc_y * delta_t
        new_vel_z = vel_z + acc_z * delta_t

        new_pos_x = pos_x + new_vel_x * delta_t
        new_pos_y = pos_y + new_vel_y * delta_t
        new_pos_z = pos_z + new_vel_z * delta_t

        updated_velocities.append((new_vel_x, new_vel_y, new_vel_z))
        updated_positions.append((new_pos_x, new_pos_y, new_pos_z))

    return updated_positions, updated_velocities


def aggregate_slices(slices: List[Tuple[int, List[Vector], List[Vector]]], total_particles: int) -> Tuple[List[Vector], List[Vector]]:
    """
    Rebuild full position and velocity arrays from worker slices.
    """
    positions = [None] * total_particles
    velocities = [None] * total_particles
    for start_index, pos_slice, vel_slice in slices:
        for offset, (position, velocity) in enumerate(zip(pos_slice, vel_slice)):
            target_index = start_index + offset
            positions[target_index] = position
            velocities[target_index] = velocity
    return positions, velocities


def compute_checksum(positions: List[Vector], velocities: List[Vector]) -> float:
    """
    Compute a simple checksum to prevent optimizations from removing work.
    """
    return sum(px + py + pz + vx + vy + vz for (px, py, pz), (vx, vy, vz) in zip(positions, velocities))


def run_nbody(num_particles: int, num_steps: int, num_workers: int, delta_t: float = 0.01, softening: float = 1e-9) -> float:
    """
    Run a naive O(N^2) N-body simulation for a fixed number of steps and return a checksum.
    """
    positions = seed_positions(num_particles)
    velocities = seed_velocities(num_particles)

    for _ in range(num_steps):
        slices: List[Tuple[int, List[Vector], List[Vector]]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_slices = {
                executor.submit(
                    compute_step_for_slice,
                    start_index,
                    end_index,
                    positions,
                    velocities,
                    delta_t,
                    softening,
                ): start_index
                for start_index, end_index in chunk_indices(num_particles, num_workers)
            }
            for future in concurrent.futures.as_completed(future_slices):
                start_index = future_slices[future]
                pos_slice, vel_slice = future.result()
                slices.append((start_index, pos_slice, vel_slice))

        positions, velocities = aggregate_slices(slices, num_particles)

    return compute_checksum(positions, velocities)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parallel N-body simulation benchmark.")
    parser.add_argument("--num_workers", required=True, type=int, help="Number of worker threads.")
    parser.add_argument("--num_particles", type=int, default=400, help="Number of particles.")
    parser.add_argument("--num_steps", type=int, default=5, help="Number of simulation steps.")
    args = parser.parse_args()

    num_workers = args.num_workers
    num_particles = args.num_particles
    num_steps = args.num_steps
    runtime_flavor = runtime_flavor_suffix()

    set_output_filename(filename=f"nbody_{num_workers}_{num_particles}_{num_steps}_{runtime_flavor}")

    set_tag("start_nbody")
    checksum = run_nbody(num_particles=num_particles, num_steps=num_steps, num_workers=num_workers)
    set_tag("finish_nbody")

    print(f"checksum: {checksum}")
