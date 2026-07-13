import unittest
from datetime import datetime
from unittest.mock import mock_open, patch

from file_manager import FileManager

from hecdss import HecDss
from hecdss.paired_data import PairedData


class TestCSV(unittest.TestCase):

    def setUp(self) -> None:
        self.test_files = FileManager()

    def tearDown(self) -> None:
        self.test_files.cleanup()

    def test_multiple_curves_to_csv(self):
        """
        This test ensures that the data values for a PairedData object with multiple curves are correct. 
        This has no checks related to units or labels.
        """
        num_curves: int = 3
        x_values: list[float] = [1.0, 1.5, 4.0]
        y_values: list[list[float]] = [[x * i for i in range(num_curves)] for x in x_values]
        labels: list[str] = [f"x times {i}" for i in range(num_curves)]
        path: str = "/A/B/C///Source: I made it up/"
        pd: PairedData = PairedData.create(
            x_values=x_values,
            y_values=y_values,
            labels=labels,
            path=path
        )

        mock_file = mock_open()
        with patch("builtins.open", mock_file):
            pd.to_csv("fake_path.csv", with_metadata=True)

        mock_file.assert_called_once_with(
            "fake_path.csv", "w", newline="", encoding="utf-8"
        )

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)

        self.assertIn("A,,A", written_data)
        self.assertIn("B,,B", written_data)
        self.assertIn("C,,C", written_data)
        self.assertIn("1,1.0,0.0,1.0,2.0", written_data)
        self.assertIn("2,1.5,0.0,1.5,3.0", written_data)
        self.assertIn("3,4.0,0.0,4.0,8.0", written_data)


if __name__ == "__main__":
    unittest.main()
