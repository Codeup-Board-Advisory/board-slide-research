import env
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


########################


def wrangle():
    # Make URL from env file
    url = f'mysql+pymysql://{env.user}:{env.password}@{env.host}/curriculum_logs'

    # Define SQL query joining log information and cohort information
    query = '''
    SELECT logs.date,
        logs.time,
        logs.path as endpoint,
        logs.user_id,
        logs.cohort_id,
        logs.ip as source_ip,
        cohorts.name as cohort_name,
        cohorts.start_date as cohort_start,
        cohorts.end_date as cohort_end,
        cohorts.program_id as program_id
    FROM logs
    JOIN cohorts ON logs.cohort_id= cohorts.id;
    '''

    # Create dataframe of query results
    print('Reading data from SQL server....')
    print('(This usually takes a while...)')
    df = pd.read_sql(query, url)
    print('Data read.')
    # Calculate how many curriculum programs an individual student has participated in.
    print('Adding number of programs completed...')
    num_programs = pd.DataFrame(df.groupby(by='user_id').cohort_id.nunique())
    df2 = df.merge(num_programs, how='inner', on='user_id')
    df2.rename(columns={'cohort_id_y': 'number_of_classes'}, inplace=True)
    df = df2.copy()

    # Concatenate date and time to new column so data can be explored more granularly, make other dates datetime objects, and re-index on datetime.
    print('Converting datatypes and reindexing on datetime....')
    df['date_time'] = df.date+' '+df.time
    df.date = pd.to_datetime(df.date)
    df.cohort_start = pd.to_datetime(df.cohort_start)
    df.cohort_end = pd.to_datetime(df.cohort_end)
    df.date_time = pd.to_datetime(df.date_time)
    df = df.set_index(df.date_time)

    # Add column for days after graduation
    print('Adding columns for days after graduation and program name.')
    df['days_after_grad'] = df.date-df.cohort_end

    # Add program description column
    valmap = {2: 'java_web_dev', 1: 'php_web_dev',
              3: 'data_science', 4: 'front_end_web_dev'}
    df['program'] = df['program_id'].map(valmap)
    print('Data is acquired, prepared, and wrangling complete.')
    return df
