"""
Hardware Abstraction Layer (HAL) for the Writer robot.

The Writer's decision logic (writer.py) only talks to this interface.
  - In Phase 1 it is implemented by SimHAL (sim_world.py).
  - In Phase 2 it is implemented by a RealHAL on the UNO Q:
        MPU (Linux/Python)  : scan(), read_thermal(), upload_log(), battery()
        MCU (via Bridge RPC): drive(), get_pose(), correct_heading(),
                              floor_distance_mm(), drop_beacon(), tilt_deg()

Conventions
  - Private frame: origin = entrance, +x = direction of entry, +y = left, angles CCW (rad).
  - Lidar angles are in the robot frame: 0 = front, +90deg = left, -90deg = right.
  - Units: metres, seconds, radians, degrees Celsius.
"""
from abc import ABC, abstractmethod
from typing import Tuple
import numpy as np


class WriterHAL(ABC):
    # ---------------- time ----------------
    @abstractmethod
    def now(self) -> float:
        """Epoch seconds (clock synced to GPS time BEFORE entering)."""

    @abstractmethod
    def step(self, dt: float) -> None:
        """Advance one control tick (sim: physics step; robot: sleep to next tick)."""

    # ---------------- actuation ----------------
    @abstractmethod
    def drive(self, v: float, w: float) -> None:
        """Command linear speed v (m/s) and turn rate w (rad/s, +left)."""

    # ---------------- proprioception ----------------
    @abstractmethod
    def get_pose(self) -> Tuple[float, float, float]:
        """Dead-reckoned pose (x, y, theta) in the private frame (wheels + IMU gyro)."""

    @abstractmethod
    def correct_heading(self, theta: float) -> None:
        """Overwrite the heading estimate (used by the LiDAR wall-alignment correction)."""

    @abstractmethod
    def measured_speed(self) -> float:
        """Forward speed measured by the wheel encoders (m/s)."""

    @abstractmethod
    def calibrate_imu(self) -> None:
        """Estimate gyro bias while the robot is standing still."""

    @abstractmethod
    def tilt_deg(self) -> float:
        """Tilt from the accelerometer (0 = flat)."""

    @abstractmethod
    def battery(self) -> float:
        """Battery level, 0..1."""

    # ---------------- exteroception ----------------
    @abstractmethod
    def scan(self) -> Tuple[np.ndarray, np.ndarray]:
        """One 360deg LiDAR scan -> (angles_rad, ranges_m), robot frame."""

    @abstractmethod
    def read_thermal(self) -> Tuple[float, float]:
        """Hottest spot in the thermal sensor's view -> (temp_C, bearing_rad relative to front)."""

    @abstractmethod
    def floor_distance_mm(self) -> float:
        """Down-facing ToF (Modulino Distance) reading ahead of the robot, in mm."""

    # ---------------- beacons and comms ----------------
    @abstractmethod
    def drop_beacon(self, message: dict) -> bool:
        """Write `message` into the next beacon by radio, release it with the servo,
        and return True only if the break-beam confirmed that it fell."""

    @abstractmethod
    def upload_log(self, log: dict) -> bool:
        """Send the log to the Outside Network Area (only possible near the entrance)."""
