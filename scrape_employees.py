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
        print("Getting main page...")
        response = session.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the login link
        print("Looking for login link...")
        login_link = soup.find('a', string='Login')
        if not login_link:
            print("Login link not found. Available links:")
            for link in soup.find_all('a'):
                print(f"- {link.get('href')}: {link.string}")
            raise Exception("Could not find login link")
        
        # Get the login page
        login_url = login_link['href']
        if not login_url.startswith('http'):
            login_url = base_url.rstrip('/') + '/' + login_url.lstrip('/')
        print(f"Found login URL: {login_url}")
        
        print("Getting login page...")
        response = session.get(login_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the login form
        print("Looking for login form...")
        login_form = soup.find('form')
        if not login_form:
            print("Login form not found. Available forms:")
            for form in soup.find_all('form'):
                print(f"- Form action: {form.get('action')}")
                print(f"  Method: {form.get('method')}")
                print(f"  Inputs: {[input.get('name') for input in form.find_all('input')]}")
            raise Exception("Could not find login form")
        
        # Get the form action URL
        form_action = login_form.get('action', '')
        if not form_action.startswith('http'):
            form_action = base_url.rstrip('/') + '/' + form_action.lstrip('/')
        print(f"Form action URL: {form_action}")
        
        # Prepare login data
        login_data = {
            'user': username,
            'pass': password
        }
        
        # Add any hidden form fields
        print("Found form fields:")
        for input_field in login_form.find_all('input'):
            name = input_field.get('name')
            type_ = input_field.get('type')
            if type_ == 'hidden':
                value = input_field.get('value', '')
                login_data[name] = value
                print(f"- Hidden field: {name}={value}")
            else:
                print(f"- Input field: {name} (type: {type_})")
        
        # Submit the login form
        print("Submitting login form...")
        response = session.post(form_action, data=login_data)
        response.raise_for_status()
        
        # Print the response URL and status
        print(f"Response URL: {response.url}")
        print(f"Response status: {response.status_code}")
        
        # Verify login was successful
        if 'login' in response.url.lower():
            print("Login page content:")
            print(response.text[:1000])  # Print first 1000 chars of response
            raise Exception("Login failed - still on login page")
        
        return True
        
    except requests.RequestException as e:
        print(f"Error during login: {e}")
        return False

def get_new_hires(session, base_url):
    """Navigate to new hires view and submit the date form"""
    try:
        # Get the report page
        print("Getting report page...")
        response = session.get(f"{base_url}/report")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find and click the "View New Hires" link
        print("Looking for View New Hires link...")
        new_hires_link = soup.find('a', string='View New Hires')
        if not new_hires_link:
            raise Exception("Could not find View New Hires link")
        
        new_hires_url = new_hires_link['href']
        if not new_hires_url.startswith('http'):
            new_hires_url = base_url.rstrip('/') + '/' + new_hires_url.lstrip('/')
        
        print(f"Getting new hires page: {new_hires_url}")
        response = session.get(new_hires_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the date form
        print("Looking for date form...")
        date_form = soup.find('form', class_='form')
        if not date_form:
            raise Exception("Could not find date form")
        
        # Get the form action URL
        form_action = date_form.get('action', '')
        if not form_action.startswith('http'):
            form_action = base_url.rstrip('/') + '/' + form_action.lstrip('/')
        
        # Prepare form data
        form_data = {
            'from': '2015-01-01',  # Jan 1, 2015
            'to': datetime.now().strftime('%Y-%m-%d'),  # Today
            'employee_ssn': ''  # Empty SSN to get all records
        }
        
        # Submit the form
        print("Submitting date form...")
        response = session.post(form_action, data=form_data)
        response.raise_for_status()
        
        return response
        
    except requests.RequestException as e:
        print(f"Error getting new hires: {e}")
        return None

def parse_employee_records(response):
    """Parse employee records from the response"""
    soup = BeautifulSoup(response.text, 'html.parser')
    employees = []
    
    # Find all employee rows
    rows = soup.find_all('tr')
    for row in rows:
        # Skip header row
        if row.find('th'):
            continue
            
        # Get all cells
        cells = row.find_all('td')
        if len(cells) >= 11:  # We expect 11 columns
            try:
                # Extract data from cells
                first_name = cells[0].text.strip()
                middle_name = cells[1].text.strip()
                last_name = cells[2].text.strip()
                suffix = cells[3].text.strip()
                ssn = cells[4].text.strip()
                address = cells[5].text.strip()
                state = cells[6].text.strip()
                hire_date = cells[7].text.strip()
                birth_date = cells[8].text.strip()
                received_date = cells[9].text.strip()
                sent_date = cells[10].text.strip()
                
                # Add to our list
                employees.append({
                    'first_name': first_name,
                    'middle_name': middle_name,
                    'last_name': last_name,
                    'suffix': suffix,
                    'ssn': ssn,
                    'address': address,
                    'state': state,
                    'hire_date': hire_date,
                    'birth_date': birth_date,
                    'received_date': received_date,
                    'sent_date': sent_date
                })
                
            except (IndexError, AttributeError) as e:
                print(f"Error parsing row: {e}")
                continue
    
    return employees

def scrape_employees():
    # Base URL
    base_url = "https://in-newhire.com"
    
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
    
    # Get new hires page
    response = get_new_hires(session, base_url)
    if not response:
        print("Failed to get new hires page. Exiting...")
        return None
    
    # Parse employee records
    employees = parse_employee_records(response)
    
    if not employees:
        print("No employee records found.")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(employees)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'employees_{timestamp}.csv'
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
    return df

if __name__ == "__main__":
    print("Starting to scrape employee data...")
    df = scrape_employees()
    if df is not None:
        print("\nEmployee Data Summary:")
        print(f"Total records found: {len(df)}")
        print("\nRecords by state:")
        print(df['state'].value_counts()) 