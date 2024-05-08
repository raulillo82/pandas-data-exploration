import pandas as pd
import requests
from bs4 import BeautifulSoup

df = pd.read_csv('salaries_by_college_major.csv')

#Print some values
#Like head command in GNU/Linux, default is 5 lines
#print(df.head())

#Check what the data looks like (returns a tuple (rows, columns)):
#print(df.shape)

#Check the columns
#(the title of them, so it gets the values from the first row):
#print(df.columns)

#Check whether it's not a number (NaN)
#print(df.isna())

#Same way there's a "head", there's a "tail"
#print(df.tail())

#Remove NaN from data:
clean_df = df.dropna()
#print(clean_df.tail())

#Get one of the fields, knowing its name:
#print(clean_df['Starting Median Salary'])
#Get the maximum of the previous search:
#print(clean_df['Starting Median Salary'].max())
#Get its index in the data:
#print(clean_df['Starting Median Salary'].idxmax())
##Get the name for that index:
#print(clean_df['Undergraduate Major'].loc[43])
#This achieves the same, double square brackets notation:
#print(clean_df['Undergraduate Major'][43])
#Get all the data from a known index:
#print(clean_df.loc[43])

############
#CHALLENGES#
############

#Q1
q1_text = """
What college major has the highest mid-career salary?
How much do graduates with this major earn?
(Mid-career is defined as having 10+ years of experience)."""
print(q1_text)
index_q1 = clean_df["Mid-Career Median Salary"].idxmax()
print(clean_df["Undergraduate Major"][index_q1])
print(clean_df["Mid-Career Median Salary"].max())

#Q2
q2_text = """
Which college major has the lowest starting salary?
How much do graduates earn after university?"""
print(q2_text)
index_q2 = clean_df["Starting Median Salary"].idxmin()
print(clean_df["Undergraduate Major"][index_q2])
print(clean_df["Starting Median Salary"].min())


#Q3
q3_text = """
Which college major has the lowest mid-career salary?
How much can people expect to earn with this degree?"""
print(q3_text)
index_q3 = clean_df["Mid-Career Median Salary"].idxmin()
print(clean_df["Undergraduate Major"][index_q3])
print(clean_df["Mid-Career Median Salary"].min())
print("")
print(clean_df.loc[index_q3])

#Low risk majors:
#print(clean_df['Mid-Career 90th Percentile Salary'] -
#      clean_df['Mid-Career 10th Percentile Salary'])
#Same as:
'''
print(clean_df['Mid-Career 90th Percentile Salary'].
      subtract(clean_df['Mid-Career 10th Percentile Salary']))
'''

#These results can be inserted into the data!
spread_col = clean_df['Mid-Career 90th Percentile Salary'] - clean_df['Mid-Career 10th Percentile Salary']
clean_df.insert(1, 'Spread', spread_col)
#print(clean_df.head())

#We can even sort the data by the new field (ascending by default, otherwise
#use "ascending=False"):
low_risk = clean_df.sort_values('Spread')
#print(low_risk[['Undergraduate Major', 'Spread']].head())

#Challenge:
q4_text = """
Using the .sort_values() method, can you find the degrees with the highest potential? Find the top 5 degrees with the highest values in the 90th percentile.
"""
print(q4_text)
high_potential = clean_df.sort_values('Mid-Career 90th Percentile Salary', ascending=False)
print(high_potential[['Undergraduate Major', 'Mid-Career 90th Percentile Salary']].head())

q5_text = """
Also, find the degrees with the greatest spread in salaries. Which majors have the largest difference between high and low earners after graduation.
"""
print(q5_text)
big_spread = clean_df.sort_values('Spread', ascending=False)
print(big_spread[['Undergraduate Major', 'Spread']].head())

q6_text= """
It's actually quite interesting to compare these two rankings versus the degrees where the median salary is very high.
"""
print(q6_text)
highly_paid = clean_df.sort_values('Mid-Career Median Salary', ascending=False)
print(highly_paid[['Undergraduate Major', 'Mid-Career Median Salary']].head())

print(clean_df.groupby('Group').count())
#Next line does not work, as not all columns are numeric
#print(clean_df.groupby('Group').mean())
#Rather use this:
#First some formatting of numbers:
pd.options.display.float_format = '{:,.2f}'.format
print(clean_df.groupby('Group')[list(clean_df.select_dtypes('number'))].mean())

q7_text = """
The PayScale dataset used in this lesson was from 2008 and looked at the prior 10 years. Notice how Finance ranked very high on post-degree earnings at the time. However, we all know there was a massive financial crash in that year. Perhaps things have changed. Can you use what you've learnt about web scraping in the prior lessons (e.g., Day 45) and share some updated information from PayScale's website in the comments below?
"""
print(q7_text)

records = []

endpoint = "https://www.payscale.com/college-salary-report/majors-that-pay-you-back/bachelors"
headers = {     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7" }
response = requests.get(endpoint, headers=headers, proxies=None)
soup = BeautifulSoup(response.text, "html.parser")
inner_btns = soup.find_all("div", {"class": "pagination__btn--inner"})
page_numbers = [inner_btn.getText() for inner_btn in inner_btns if inner_btn.getText().isnumeric()]
try:
    total_pages = int(max(page_numbers))
    #print(total_pages)

    for current_page in range(total_pages):
        endpoint = f"{endpoint}/page/{current_page + 1}"
        response = requests.get(endpoint, headers=headers, proxies=None)
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("table.data-table tbody tr")
        for row in rows:
            cells = row.select("span.data-table__value")
            record = {
                "Undergraduate Major": cells[1].getText(),
                "Starting Median Salary": float(cells[3].getText().strip("$").replace(",", "")),
                "Mid-Career Median Salary": float(cells[4].getText().strip("$").replace(",", "")),
            }
            records.append(record)

    pd.DataFrame(records).to_csv("salaries_by_college_major_updated.csv", index=False)
except ValueError:
    print(f"Page could not be scrapped, reponse code html {response.status_code}")
    print("""Trying to use possible previously saved results from the file
    salaries_by_college_major_updated.csv""")
finally:
    try:
        df2 = pd.read_csv("salaries_by_college_major_updated.csv")
        print(df2)
    except FileNotFoundError:
        print("""File salaries_by_college_major_updated.csv could not be generated
        AND it did not exist in the disk either""")
