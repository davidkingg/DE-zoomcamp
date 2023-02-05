
import pandas as pd
from time import time
from sqlalchemy import create_engine, text
import argparse
import os


def main(params):
    user = params.user
    password = params.password
    host = params.host
    db = params.db
    port = params.port
    table = params.table_name
    file =  params.file_path

    engine=create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()

    try:
        df=pd.read_parquet(f'{file}', engine = 'fastparquet')
    except:
        file = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet'
        print('downloading data')
        os.system(f'wget {file} -O {file}')
        df=pd.read_parquet(f'{file}', engine = 'fastparquet')
    df.to_csv('taxi_data.csv', index=False)
    print(pd.io.sql.get_schema(df,'taxi data'))

    df_iter = pd.read_csv('taxi_data.csv',chunksize=100000, iterator=True,parse_dates=['tpep_pickup_datetime','tpep_dropoff_datetime'])
    # this creates a schema for the table
    next(df_iter).head(0).to_sql(name=f'{table}', con=engine, if_exists='replace',index=False)


    while True:
        try:
            start_time = time()
            next(df_iter).to_sql(name=f'{table}', con=engine, if_exists='append',index=False)
            end_time = time()

            print('finished appending %.3f' % (end_time - start_time))
        except:
            break

    print('finished loading all the data to posgresql')
    pd.DataFrame(engine.connect().execute(text(f'select * from {table} limit 5')))

    
if __name__== '__main__':
    parser = argparse.ArgumentParser(description='data ingesting')
    parser.add_argument('--port',type=int,help='postgres connection port')
    parser.add_argument('--table_name' ,help='destination table name')
    parser.add_argument('--user' ,help='postgres user')
    parser.add_argument('--db' ,help='database name')
    parser.add_argument('--password' ,help='database password')
    parser.add_argument('--host' ,help='connection host')
    parser.add_argument('--file_path' ,help='path to parquet file')
    #parser.add_argument('table_name' ,help='an integer for the accumulator')
    args = parser.parse_args()
    main(args)


## runcode 
# python postgres_data_loading.py --port=5432 --table_name=test --user=test --db=test --password=test --host=localhost --file_path=yellow_tripdata_2021-01.parquet


