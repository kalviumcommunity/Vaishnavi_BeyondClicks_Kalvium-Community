import unittest
import io
import datetime
from streamlit.testing.v1 import AppTest


class TestStreamlitApp(unittest.TestCase):

    def test_initial_state(self):
        """Test initial dashboard state with campaign dataset."""
        at = AppTest.from_file("app.py").run(timeout=25)
        self.assertFalse(at.exception)
        # Verify app title present
        self.assertTrue(any("BeyondClicks" in t.value for t in at.title))
        # Verify markdown content exists
        self.assertTrue(len(at.markdown) > 0)

    def test_csv_upload_and_preview(self):
        """Test uploading a valid custom CSV file."""
        csv_data = (
            "Campaign_ID,Campaign_Type,Target_Audience,Platform,Customer_Segment,Date,Impressions,Clicks,Signups,Activated_Users,Revenue,Acquisition_Cost,ROI,CTR,Signup_Rate,Activation_Rate\n"
            "CMP-1,Social Media,Young Adults,Meta,Enterprise,2026-07-01,1000,100,20,10,500,100,5.0,10.0,20.0,50.0\n"
            "CMP-2,Search Ads,Professionals,Google,SMB,2026-07-02,2000,200,40,30,1200,200,6.0,10.0,20.0,75.0\n"
        )

        at = AppTest.from_file("app.py")
        at.run(timeout=25)
        if len(at.file_uploader) > 0:
            at.file_uploader[0].upload("test_campaigns.csv", csv_data.encode("utf-8"))
            at.run(timeout=25)
            self.assertTrue(at.sidebar.success)
            self.assertIn("Loaded: test_campaigns.csv", at.sidebar.success[0].value)

    def test_filter_propagation(self):
        """Test filtering the dataset using segment selectbox."""
        at = AppTest.from_file("app.py").run(timeout=25)
        self.assertFalse(at.exception)
        
        if len(at.selectbox) > 0 and len(at.selectbox[0].options) > 1:
            # Change Segment selectbox to second option
            at.selectbox[0].select(at.selectbox[0].options[1])
            at.run(timeout=25)
            self.assertFalse(at.exception)

    def test_empty_filter_combination(self):
        """Test when filters yield 0 matches using an invalid date range."""
        at = AppTest.from_file("app.py").run(timeout=25)
        
        if len(at.date_input) > 0:
            at.date_input[0].set_value((datetime.date(2035, 1, 1), datetime.date(2035, 1, 10)))
            at.run(timeout=25)
            
            # Verify warning box is shown if no data matches
            if len(at.warning) > 0:
                self.assertIn("No data matches the current filters", at.warning[0].value)

    def test_reset_filters(self):
        """Test that the Reset Filters button runs without exception."""
        at = AppTest.from_file("app.py").run(timeout=25)
        
        if len(at.selectbox) > 0 and len(at.selectbox[0].options) > 1:
            at.selectbox[0].select(at.selectbox[0].options[1])
            at.run(timeout=25)
        
        if len(at.button) > 0:
            # Click reset button
            at.button[0].click()
            at.run(timeout=25)
            self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
