import requests
import pandas as pd

def scrape_api_data(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if 'records' in data:
            df = pd.DataFrame(data['records'])
            
            # Save to CSV
            df.to_csv('api_data.csv', index=False)
            print("Data scraped and saved to 'api_data.csv'")
            
            # Display first few rows
            print(df.head())
        else:
            print("No records found in the API response")
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

# API URL
api_url = "https://loadqa.ndapapi.com/v1/openapi?API_Key=gAAAAABm_xn3atE6lYlNOfgqsbsVb-TlQFY3TSV8Dfk-RAO3rdLSAPvs97QtOhha2mTZbkgl6j76B8En70O3A2J6drCnIsrRvJJPgYn23a4gB9BeiFaTJgS90u_vz39Kys2_Fr4EW9zM9G9fxa6y4N3g3ANwDS66rb_yDnJ9oUeFjTsIpzCaNQT3AU7oEU28ga_x582rdIsQ&ind=I1087_5&dim=Country,Year,D1087_3,D1087_4,D1087_6&pageno=1"

# Call the function to scrape data
scrape_api_data(api_url)