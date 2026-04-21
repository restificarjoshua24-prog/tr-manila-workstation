"""
Microsoft Outlook/365 Calendar Integration Module
"""
import requests
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication


class OutlookCalendar:
    """Handle Microsoft Outlook calendar integration"""
    
    def __init__(self, config):
        self.config = config
        self.client_id = config.get('CLIENT_ID')
        self.client_secret = config.get('CLIENT_SECRET')
        self.tenant_id = config.get('TENANT_ID')
        self.authority = config.get('AUTHORITY')
        self.scope = config.get('SCOPE')
        
        if self.client_id and self.client_secret and self.tenant_id:
            self.app = ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
        else:
            self.app = None
    
    def get_access_token(self):
        """Get access token for Microsoft Graph API"""
        if not self.app:
            return None
        
        try:
            result = self.app.acquire_token_for_client(scopes=self.scope)
            if 'access_token' in result:
                return result['access_token']
            else:
                print(f"Failed to acquire token: {result.get('error_description')}")
                return None
        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None
    
    def create_calendar_event(self, user_email, subject, start_datetime, end_datetime, location, body):
        """
        Create a calendar event in user's Outlook calendar
        
        Args:
            user_email: User's email address
            subject: Event subject/title
            start_datetime: Start datetime
            end_datetime: End datetime
            location: Event location
            body: Event body/description
            
        Returns:
            Event ID if successful, None otherwise
        """
        token = self.get_access_token()
        if not token:
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # Format datetime for Microsoft Graph API
        start_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        end_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        
        event_data = {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': body
            },
            'start': {
                'dateTime': start_str,
                'timeZone': 'Asia/Manila'
            },
            'end': {
                'dateTime': end_str,
                'timeZone': 'Asia/Manila'
            },
            'location': {
                'displayName': location
            },
            'attendees': [
                {
                    'emailAddress': {
                        'address': user_email,
                        'name': user_email.split('@')[0]
                    },
                    'type': 'required'
                }
            ],
            'isReminderOn': True,
            'reminderMinutesBeforeStart': 60,
            'categories': ['Workstation Booking']
        }
        
        try:
            # Create event in user's calendar
            url = f'https://graph.microsoft.com/v1.0/users/{user_email}/events'
            response = requests.post(url, headers=headers, json=event_data)
            
            if response.status_code == 201:
                event = response.json()
                return event.get('id')
            else:
                print(f"Failed to create calendar event: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error creating calendar event: {str(e)}")
            return None
    
    def update_calendar_event(self, user_email, event_id, subject=None, start_datetime=None, end_datetime=None, location=None, body=None):
        """Update an existing calendar event"""
        token = self.get_access_token()
        if not token:
            return False
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        update_data = {}
        
        if subject:
            update_data['subject'] = subject
        
        if start_datetime:
            update_data['start'] = {
                'dateTime': start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Asia/Manila'
            }
        
        if end_datetime:
            update_data['end'] = {
                'dateTime': end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': 'Asia/Manila'
            }
        
        if location:
            update_data['location'] = {'displayName': location}
        
        if body:
            update_data['body'] = {
                'contentType': 'Text',
                'content': body
            }
        
        try:
            url = f'https://graph.microsoft.com/v1.0/users/{user_email}/events/{event_id}'
            response = requests.patch(url, headers=headers, json=update_data)
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating calendar event: {str(e)}")
            return False
    
    def delete_calendar_event(self, user_email, event_id):
        """Delete a calendar event"""
        token = self.get_access_token()
        if not token:
            return False
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        try:
            url = f'https://graph.microsoft.com/v1.0/users/{user_email}/events/{event_id}'
            response = requests.delete(url, headers=headers)
            
            return response.status_code == 204
        except Exception as e:
            print(f"Error deleting calendar event: {str(e)}")
            return False
    
    def get_user_calendar_events(self, user_email, start_date=None, end_date=None):
        """Get user's calendar events within a date range"""
        token = self.get_access_token()
        if not token:
            return []
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        # Default to current month if no dates provided
        if not start_date:
            start_date = datetime.now().replace(day=1)
        if not end_date:
            end_date = start_date + timedelta(days=31)
        
        start_str = start_date.strftime('%Y-%m-%dT00:00:00')
        end_str = end_date.strftime('%Y-%m-%dT23:59:59')
        
        try:
            url = f'https://graph.microsoft.com/v1.0/users/{user_email}/calendarView'
            params = {
                'startDateTime': start_str,
                'endDateTime': end_str,
                '$select': 'subject,start,end,location,categories',
                '$orderby': 'start/dateTime'
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            else:
                print(f"Failed to get calendar events: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting calendar events: {str(e)}")
            return []