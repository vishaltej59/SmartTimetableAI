import unittest
from unittest.mock import patch, MagicMock
from app.services.calendar_service import check_schedule_conflicts

class TestConflicts(unittest.TestCase):

    @patch('app.services.calendar_service.get_calendar_service')
    def test_full_overlap(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock Google API response with a conflicting event
        mock_service.events().list().execute.return_value = {
            'items': [{
                'summary': 'Existing Class',
                'start': {'dateTime': '2026-06-13T10:00:00+05:30'},
                'end': {'dateTime': '2026-06-13T12:00:00+05:30'}
            }]
        }
        
        result = check_schedule_conflicts('2026-06-13T10:30:00+05:30', '2026-06-13T11:30:00+05:30')
        self.assertTrue(result['conflict'])
        self.assertEqual(result['event_title'], 'Existing Class')

    @patch('app.services.calendar_service.get_calendar_service')
    def test_partial_overlap(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock Google API response with a conflicting event
        mock_service.events().list().execute.return_value = {
            'items': [{
                'summary': 'Another Meeting',
                'start': {'dateTime': '2026-06-13T14:00:00+05:30'},
                'end': {'dateTime': '2026-06-13T15:30:00+05:30'}
            }]
        }
        
        result = check_schedule_conflicts('2026-06-13T13:00:00+05:30', '2026-06-13T14:30:00+05:30')
        self.assertTrue(result['conflict'])

    @patch('app.services.calendar_service.get_calendar_service')
    def test_no_overlap(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock Google API returning empty items list
        mock_service.events().list().execute.return_value = {
            'items': []
        }
        
        result = check_schedule_conflicts('2026-06-13T16:00:00+05:30', '2026-06-13T17:00:00+05:30')
        self.assertFalse(result['conflict'])

if __name__ == '__main__':
    unittest.main()
