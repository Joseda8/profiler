from enum import Enum
from typing import List
import subprocess


class EnergyUnit(Enum):
    UNIT = "J"
    MILI = "mJ"
    MICRO = "µJ"


class EnergyStatsCollector:
    """
    A class for measuring global system energy via powercap-info.
    """

    def __init__(self):
        """
        Initialize by detecting the PSys zone and its wrap limit (µJ).
        """
        self._psys_zone_index = self._find_psys_zone()
        self._psys_max_energy_uj = self._read_zone_max_energy_uj(self._psys_zone_index)

    @staticmethod
    def _run_powercap_info(args: List[str]) -> str:
        """
        Run the powercap-info command with given arguments.

        Args:
            args (List[str]): List of arguments to pass to powercap-info.

        Returns:
            str: Standard output from the executed command.
        """
        out = subprocess.run(
            ["sudo", "powercap-info", "intel-rapl"] + args,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return out

    @classmethod
    def _num_top_zones(cls) -> int:
        """
        Get the number of top-level RAPL zones.

        Returns:
            int: Number of top-level zones.
        """
        return int(cls._run_powercap_info(["-n"]))

    @classmethod
    def _zone_name(cls, zone_index: int) -> str:
        """
        Get the name of a zone by its index.

        Args:
            zone_index (int): Index of the zone.

        Returns:
            str: Name of the zone.
        """
        return cls._run_powercap_info(["-z", str(zone_index), "-x"])

    @classmethod
    def _find_psys_zone(cls) -> int:
        """
        Find the index of the PSys zone.

        Returns:
            int: Index of the PSys zone.

        Raises:
            RuntimeError: If PSys zone is not found.
        """
        total_zones = cls._num_top_zones()
        for zone_index in range(total_zones):
            if cls._zone_name(zone_index).strip().lower() == "psys":
                return zone_index
        raise RuntimeError(
            "PSys zone not found. Cannot measure system-wide energy via RAPL."
        )

    @classmethod
    def _read_zone_energy_uj(cls, zone_index: int) -> int:
        """
        Read the current energy value for a given zone.

        Args:
            zone_index (int): Index of the zone.

        Returns:
            int: Energy in microjoules (µJ).
        """
        return int(cls._run_powercap_info(["-z", str(zone_index), "-j"]))

    @classmethod
    def _read_zone_max_energy_uj(cls, zone_index: int) -> int:
        """
        Read the maximum energy value before wraparound for a given zone.

        Args:
            zone_index (int): Index of the zone.

        Returns:
            int: Maximum energy in microjoules (µJ) before wraparound.
        """
        return int(cls._run_powercap_info(["-z", str(zone_index), "-J"]))

    def read_energy(self) -> float:
        """
        Read the current PSys energy value.

        Returns:
            float: Energy in Joules (µJ).
        """
        return self._read_zone_energy_uj(self._psys_zone_index)

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
