import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

def scrape_employees():
    # Base URL
    base_url = "https://in-newhire.com"
    
    # Initialize lists to store data
    employees = []
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the request
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
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