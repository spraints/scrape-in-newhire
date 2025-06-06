import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import getpass

def login(session, base_url, username, password):
    """Handle the login process"""
    try:
        # Get the main page to find the login link
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the login link
        login_link = soup.find('a', text='Login')
        if not login_link:
            raise Exception("Could not find login link")
        
        # Get the login page
        login_url = login_link['href']
        if not login_url.startswith('http'):
            login_url = base_url.rstrip('/') + '/' + login_url.lstrip('/')
        
        response = session.get(login_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the login form
        login_form = soup.find('form')
        if not login_form:
            raise Exception("Could not find login form")
        
        # Get the form action URL
        form_action = login_form.get('action', '')
        if not form_action.startswith('http'):
            form_action = base_url.rstrip('/') + '/' + form_action.lstrip('/')
        
        # Prepare login data
        login_data = {
            'username': username,
            'password': password
        }
        
        # Add any hidden form fields
        for hidden in login_form.find_all('input', type='hidden'):
            login_data[hidden.get('name')] = hidden.get('value', '')
        
        # Submit the login form
        response = session.post(form_action, data=login_data)
        response.raise_for_status()
        
        # Verify login was successful
        if 'login' in response.url.lower():
            raise Exception("Login failed - still on login page")
        
        return True
        
    except requests.RequestException as e:
        print(f"Error during login: {e}")
        return False

def scrape_employees():
    # Base URL
    base_url = "https://in-newhire.com"
    
    # Initialize lists to store data
    employees = []
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Create a session to maintain cookies
    session = requests.Session()
    session.headers.update(headers)
    
    # Get login credentials
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    
    # Perform login
    if not login(session, base_url, username, password):
        print("Failed to login. Exiting...")
        return None
    
    try:
        # Make the request to the main page after login
        response = session.get(base_url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all employee entries
        # Note: You'll need to adjust these selectors based on the actual HTML structure
        employee_entries = soup.find_all('div', class_='employee-entry')
        
        for entry in employee_entries:
            try:
                # Extract employee information
                # Note: Adjust these selectors based on the actual HTML structure
                name = entry.find('h2', class_='employee-name').text.strip()
                status = entry.find('span', class_='status').text.strip()
                date = entry.find('span', class_='date').text.strip()
                
                # Add to our list
                employees.append({
                    'name': name,
                    'status': status,
                    'date': date
                })
                
            except AttributeError as e:
                print(f"Error parsing employee entry: {e}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(employees)
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'employees_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
        return df
        
    except requests.RequestException as e:
        print(f"Error fetching the website: {e}")
        return None

if __name__ == "__main__":
    print("Starting to scrape employee data...")
    df = scrape_employees()
    if df is not None:
        print("\nEmployee Data Summary:")
        print(f"Total records found: {len(df)}")
        print("\nStatus distribution:")
        print(df['status'].value_counts()) 