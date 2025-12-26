from enum import Enum
from pathlib import Path
from typing import Tuple


class EnergyUnit(Enum):
    UNIT = "J"
    MILI = "mJ"
    MICRO = "µJ"


class EnergyStatsCollector:
    """
    A class for measuring global system energy via RAPL sysfs files.
    """

    def __init__(self):
        """
        Initialize by detecting the PSys zone and its wrap limit (µJ).
        """
        _, energy_file, max_energy_file = self._locate_psys_zone()
        self._energy_fd = self._open_energy_file(energy_file)
        self._psys_max_energy_uj = self._read_int_file(max_energy_file)

    @staticmethod
    def _read_int_file(path: Path) -> int:
        """
        Read an integer from a sysfs file.
        """
        try:
            return int(path.read_text().strip())
        except FileNotFoundError:
            raise RuntimeError(f"Required energy file not found: {path}")
        except Exception as excep:
            raise RuntimeError(f"Failed reading {path}: {excep}")

    @staticmethod
    def _locate_psys_zone() -> Tuple[Path, Path, Path]:
        """
        Locate the PSys RAPL zone under /sys/class/powercap and return
        the key paths needed for energy reading.

        Returns:
            Tuple containing:
                - psys_path (Path): The PSys zone directory.
                - energy_file (Path): The energy_uj file within that zone.
                - max_energy_file (Path): The max_energy_range_uj file.
        """
        root = Path("/sys/class/powercap")
        if not root.exists():
            raise RuntimeError("RAPL sysfs path not found (/sys/class/powercap).")

        queue = list(root.glob("intel-rapl:*"))
        while queue:
            zone = queue.pop(0)
            name_file = zone / "name"
            try:
                name = name_file.read_text().strip().lower()
            except Exception:
                name = ""

            if name == "psys":
                energy_file = zone / "energy_uj"
                max_energy_file = zone / "max_energy_range_uj"
                return zone, energy_file, max_energy_file

            # Explore nested zones
            queue.extend(zone.glob("intel-rapl:*"))

        raise RuntimeError("PSys zone not found under /sys/class/powercap.")

    def _open_energy_file(self, energy_file: Path):
        """
        Open the energy file descriptor for fast repeated reads.
        """
        try:
            return energy_file.open("r")
        except Exception as excep:
            raise RuntimeError(f"Failed to open energy file {energy_file}: {excep}")

    def _read_energy_uj(self) -> int:
        """
        Read the current energy value for the PSys zone in µJ.
        """
        self._energy_fd.seek(0)
        return int(self._energy_fd.read().strip())

    def read_energy(self) -> float:
        """
        Read the current PSys energy value.

        Returns:
            float: Energy in Joules (µJ).
        """
        return self._read_energy_uj()

    def energy_delta(
        self,
        start_energy_uj: float,
        end_energy_uj: float,
        unit: EnergyUnit = EnergyUnit.MICRO,
    ) -> float:
        """
        Compute the energy delta between two readings,
        handling wraparound using the hardware-reported maximum.

        Args:
            start_energy_uj (float): Starting energy reading in microjoules (µJ).
            end_energy_uj (float): Ending energy reading in microjoules (µJ).
            unit (EnergyUnit): Desired output unit (J, mJ, µJ). Default = µJ.

        Returns:
            float: Energy difference in the requested unit.
        """
        if end_energy_uj >= start_energy_uj:
            delta_uj = end_energy_uj - start_energy_uj
        else:
            delta_uj = (self._psys_max_energy_uj - start_energy_uj) + end_energy_uj

        if unit == EnergyUnit.UNIT:
            return delta_uj / 1e6
        elif unit == EnergyUnit.MILI:
            return delta_uj / 1e3
        elif unit == EnergyUnit.MICRO:
            return delta_uj
        else:
            raise ValueError(f"Unsupported energy unit: {unit}")
