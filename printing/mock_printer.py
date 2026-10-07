from .printer import Printer


class MockPrinter(Printer):

    def print_qr(
        self,
        data: str,
        width_mm: float,
        height_mm: float,
        qr_size_mm: float,
        quantity: int,
    ):
        print()
        print("========== MOCK PRINT ==========")
        print(f"Data:       {data}")
        print(f"Label:      {width_mm} × {height_mm} mm")
        print(f"QR size:    {qr_size_mm} mm")
        print(f"Quantity:   {quantity}")
        print("================================")
        print()