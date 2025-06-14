import requests
from bs4 import BeautifulSoup
import pandas as pd

# Target URL
url = "https://weworkremotely.com/categories/remote-programming-jobs"

# Send GET request
headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)

# Parse HTML
soup = BeautifulSoup(response.text, "html.parser")

# Find job listings
jobs = soup.find_all("section", class_="jobs")

data = []

for section in jobs:
    listings = section.find_all("li", class_=lambda x: x != "view-all")
    for job in listings:
        try:
            company = job.find("span", class_="company").text.strip()
            title = job.find("span", class_="title").text.strip()
            link = "https://weworkremotely.com" + job.find("a")["href"]

            data.append({
                "Company": company,
                "Job Title": title,
                "Link": link
            })
        except AttributeError:
            continue  # Skip malformed job cards

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("remote_jobs.csv", index=False)

print("✅ Scraping complete. Data saved to remote_jobs.csv")
