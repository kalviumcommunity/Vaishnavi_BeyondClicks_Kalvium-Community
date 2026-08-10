import unittest
import io
from streamlit.testing.v1 import AppTest

class TestStreamlitApp(unittest.TestCase):

    def test_initial_state(self):
        """Test initial dashboard state when no file is uploaded."""
        at = AppTest.from_file("app.py").run(timeout=15)
        # Verify info message is shown
        self.assertTrue(at.info)
        self.assertEqual(at.info[0].value, "Upload a CSV or JSON file to begin.")

    def test_csv_upload(self):
        """Test uploading a valid CSV file."""
        csv_data = "a,b,c\n1,2,3\n4,5,6\n"
        
        at = AppTest.from_file("app.py")
        # Run first to let the file uploader widget instantiate
        at.run(timeout=15)
        at.file_uploader[0].upload("test.csv", csv_data.encode("utf-8"))
        at.run(timeout=15)
        
        # Verify success message and preview headers
        self.assertTrue(at.success)
        self.assertIn("Loaded: test.csv", at.success[0].value)
        self.assertTrue(any(h.value == "Dataset Preview" for h in at.header))
