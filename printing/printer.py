from abc import ABC, abstractmethod


class Printer(ABC):

    @abstractmethod
    def print_qr(
        self,
        data: str,
        width_mm: float,
        height_mm: float,
        qr_size_mm: float,
        quantity: int,
    ):
        pass