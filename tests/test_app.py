import unittest
import io
import datetime
from streamlit.testing.v1 import AppTest

class TestStreamlitApp(unittest.TestCase):

    def test_initial_state(self):
        """Test initial dashboard state with default seed dataset."""
        at = AppTest.from_file("app.py").run(timeout=15)
        # Verify preview header is present
        self.assertTrue(any(h.value == "Dataset Preview" for h in at.header))
        # Default rows count metric
        self.assertEqual(at.metric[0].value, "100")

    def test_csv_upload_and_preview(self):
        """Test uploading a valid CSV file."""
        csv_data = "date,segment,revenue\n2026-07-01,Enterprise,1000\n2026-07-02,SMB,500\n2026-07-03,Startup,250\n"
        
        at = AppTest.from_file("app.py")
        at.run(timeout=15)
        at.file_uploader[0].upload("test.csv", csv_data.encode("utf-8"))
        at.run(timeout=15)
        
        # Verify success message and rows count metric
        self.assertTrue(at.success)
        self.assertIn("Loaded: test.csv", at.success[0].value)
        self.assertEqual(at.metric[0].value, "3")

    def test_filter_propagation(self):
        """Test filtering the dataset using the widgets."""
        at = AppTest.from_file("app.py").run(timeout=15)
        
        # Initial rows: 100
        self.assertEqual(at.metric[0].value, "100")
        
        # Change Segment to select only 'Enterprise'
        at.multiselect[0].set_value(["Enterprise"])
        at.run(timeout=15)
        
        # Verify row count metric is reduced
        rows_val = int(at.metric[0].value.replace(",", ""))
        self.assertLess(rows_val, 100)
        self.assertGreater(rows_val, 0)

    def test_empty_filter_combination(self):
        """Test when filters yield 0 matches."""
        at = AppTest.from_file("app.py").run(timeout=15)
        
        # Set impossible date range (e.g. 2028 dates)
        at.date_input[0].set_value((datetime.date(2028, 1, 1), datetime.date(2028, 1, 10)))
        at.run(timeout=15)
        
        # Verify warning box is shown
        self.assertTrue(at.warning)
        self.assertIn("No data matches the current filters", at.warning[0].value)

    def test_reset_filters(self):
        """Test that the Reset Filters button restores defaults."""
        at = AppTest.from_file("app.py").run(timeout=15)
        
        # Modify some values
        at.multiselect[0].set_value(["Enterprise"])
        at.run(timeout=15)
        self.assertNotEqual(at.metric[0].value, "100")
        
        # Click reset button
        at.button[0].click()
        at.run(timeout=15)
        
        # Value should return to default (100 rows)
        self.assertEqual(at.metric[0].value, "100")
