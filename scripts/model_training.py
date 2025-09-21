"""Utility script to bootstrap the layered quant research stack."""
from __future__ import annotations

from quant_platform import (
    ArchitectureOptimiser,
    HardwareAdapter,
    PlatformConfig,
    ResearchCoordinator,
)


def main() -> None:
    config = PlatformConfig()
    hardware = HardwareAdapter(config.hardware)
    optimiser = ArchitectureOptimiser(frameworks=["FastAPI", "Prefect", "Ray"])
    research = ResearchCoordinator()

    print("Hardware profile:", hardware.summary())
    print("Architecture reflection:", optimiser.run_reflection(["高频回测", "多模态研究"]).__dict__)
    print("Research preview:", research.run_auto_research("Chan theory"))


if __name__ == "__main__":
    main()
