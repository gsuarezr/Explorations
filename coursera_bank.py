# Code for ETL operations on Country-GDP data
# Importing the required libraries
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sqlite3



def log_progress(message):
    ''' This function logs the mentioned message of a given stage of the
    code execution to a log file. Function returns nothing'''
    file_path = 'code_log.txt'
    # Open the file in append mode, create it if it doesn't exist
    with open(file_path, 'a') as file:
        file.write(str(time.time())+':'+message+'\n')

def extract(url, table_attribs):
    ''' This function aims to extract the required
    information from the website and save it to a data frame. The
    function returns the data frame for further processing. '''
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    tables = soup.find_all('tbody')
    rows = tables[0].find_all('tr')
    df = pd.DataFrame(columns=table_attribs)    
    for row in rows:
        col = row.find_all('td')
        if len(col)!=0:
            data_dict = {"Name": col[1].find_all('a',title=True)[-1]['title'],
                        "MC_USD_Billion": float(col[2].contents[0].replace('\n', ''))}
            df1 = pd.DataFrame(data_dict, index=[0])
            df = pd.concat([df,df1], ignore_index=True)
        else:
            pass
    return df

def transform(df, csv_path):
    ''' This function accesses the CSV file for exchange rate
    information, and adds three columns to the data frame, each
    containing the transformed version of Market Cap column to
    respective currencies'''
    dataframe= pd.read_csv(csv_path)
    dictio = dataframe.set_index('Currency').to_dict()['Rate']
    df['MC_EUR_Billion']=(dictio['EUR']*df['MC_USD_Billion']).round(2)
    df['MC_GBP_Billion']=(dictio['GBP']*df['MC_USD_Billion']).round(2)
    df['MC_INR_Billion']=(dictio['INR']*df['MC_USD_Billion']).round(2)
    return df

def load_to_csv(df, output_path):
    ''' This function saves the final data frame as a CSV file in
    the provided path. Function returns nothing.'''
    df.to_csv(output_path,index=False)
    log_progress("Dataframe CSV has been created")
def load_to_db(df, sql_connection, table_name):
    ''' This function saves the final data frame to a database
    table with the provided name. Function returns nothing.'''
    df.to_sql(table_name, sql_connection, if_exists='replace', index=False)
    log_progress("Dataframe now in the database")

def run_query(query_statement, sql_connection):
    ''' This function runs the query on the database table and
    prints the output on the terminal. Function returns nothing. '''
    df = pd.read_sql(query_statement, sql_connection)
    print(df)

''' Here, you define the required entities and call the relevant
functions in the correct order to complete the project. Note that this
portion is not inside any function.'''
if __name__=="__main__":
    url='https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
    df=extract(url,["Name","MC_USD_Billion"])
    df=transform(df,'exchange_rate.csv')
    load_to_csv(df,"Largest_banks_data.csv")
    con=sqlite3.connect("Banks.db")
    load_to_db(df,con,"Largest_banks")
    run_query("SELECT * FROM Largest_banks",con)
    run_query("SELECT AVG(MC_GBP_Billion) FROM Largest_banks",con)
    run_query("SELECT Name from Largest_banks LIMIT 5",con)
