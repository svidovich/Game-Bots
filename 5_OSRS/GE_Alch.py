import requests

from bs4 import BeautifulSoup

import pandas as pd


# URL of the webpage containing the chart

url = "https://oldschool.runescape.wiki/w/RuneScape:Grand_Exchange_Market_Watch/Alchemy"


# Define a headers dictionary with a User-Agent

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}


# Send a GET request to the URL with the headers

response = requests.get(url, headers=headers)


# Check if the request was successful

if response.status_code == 200:
    # Parse the content of the response
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the table (replace 'your-class-name' with the correct class if necessary)
    table = soup.find('table', class_='wikitable')  # Adjust as necessary

    # Initialize a list to store the data
    data = []

    # Loop through each row in the table
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) > 0:  # Ensure there are columns to read
            item_data = [col.text.strip() for col in cols]

            # Initialize Members status as 0 (non-members) by default
            members_status = 0

            # Check if there's a link indicating the item is for members
            for col in cols:
                if col.find('a') and 'Members' in col.find('a')['href']:
                    members_status = 1
                    break

            # Append the item data along with the members status
            item_data.append(members_status)
            data.append(item_data)


    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=['Picture', 'Item', 'GE Price', 'High Alch', 'Profit', 'ROI%', 'Limit', 'Volume',
                                      'Max Profit', 'Profit per Minute', 'Junk', 'Details', 'Members'])

    df = df.drop('Picture', axis=1)
    df = df.drop('Junk', axis=1)
    df = df.drop('Details', axis=1)
    
    non_members_df = df[df['Members'] == 0]
    non_members_df["Profit"] = pd.to_numeric(non_members_df["Profit"])
    sorted_non_members_df = non_members_df.sort_values(by='Profit', ascending=False)

    # Print the DataFrame
    # print(sorted_non_members_df)

    for i in range(10):
        TopItem = sorted_non_members_df.iloc[i]["Item"]
        print("Top Item " + str(i) + " is: " + TopItem)

    # Optionally, save the DataFrame to a CSV file
    sorted_non_members_df.to_csv('alchemy_data.csv', index=False)
else:
    print(f"Failed to retrieve the page, status code: {response.status_code}")