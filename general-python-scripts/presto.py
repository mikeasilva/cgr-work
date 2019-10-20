# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:30:34 2018

@author: Michael Silva
"""
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

class Hub(object):
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://user:password@server/database')
        self.engine_connect = self.engine.connect()
    def connection(self):
        return(self.engine_connect)
    def disconnect(self):
        self.engine_connect.close()
    def query(self, sql):
        return self.engine_connect.execute(sql)
    def save(self, df, table_name):
        df.to_sql(table_name, con=self.engine, if_exists = 'replace', index = False)
    

def aggregate_acs_data(df, var_list, return_float=False):
    """Aggregate estimates and margins of error specified in var_list and
    found in df and return a list with the aggregated estimate and margin
    of error"""
    est = list()
    moe = list()
    if var_list is False:
        return [None, None]
    for v in var_list:
        est.append(v+'E')
        moe.append(v+'M')
    agg = aggregate_census_data(df, est, return_float)
    # Sum of squares
    agg_moe = df[moe] ** 2
    # Square root of the sum of squares
    agg_moe = agg_moe.sum(axis=1) ** .5
    agg_moe = agg_moe.astype('float64')
    return {'est': agg['est'], 'moe': agg_moe}

def aggregate_census_data(df, var_list, return_float=False):
    """Aggregate data specified in var_list and found in df"""
    agg = df[var_list].sum(axis=1)
    if return_float:
        return {'est': agg.astype('float64')}
    else:
        return {'est': agg.astype('int64')}
    
def get_cpi_inflator(year, base_year):
    """Get's the inflator for a year givent the base_year.
    
    Parameters
        ----------
        year : int
            The year the dollars are in
        base_year : int
            The year you want the dollars inflated to
            
    Returns
        -------
        inflator : float
            The multiplier to adjust for inflation
    """
    # Pull the CPI table from the hub
    hub = Hub()
    a = hub.query('SELECT * FROM US_CPIInflator_BLS WHERE `year` = '+str(year))
    cpi = a.fetchone()[0]
    b = hub.query('SELECT * FROM US_CPIInflator_BLS WHERE `year` = '+str(base_year))
    base_cpi = b.fetchone()[0]
    inflator = base_cpi / cpi
    return inflator
    
    
def get_cpi_year():
    """Reads the CPI year from Set CPI Year.R."""
    with open('Set CPI Year.R') as f:
        for cnt, line in enumerate(f):
            if 'cpi_year <- ' in line:
                line = line.replace('cpi_year <- ','')
                return int(line)
            

def get_sum_aggregates(df, aggregate_me):
    # Get geographies in data frame
    geos = df.geo_id.unique()
    # Build a data frame of geographies to aggreate
    aggregate_data = list()
    for a in aggregate_me:
        if a[1] not in geos:
            aggregate_data.append({'geo_id': a[0], 'aggregate_id': a[1]})
    aggregate_data = pd.DataFrame(aggregate_data)
    
    # Merge it with our data (inner join)
    df = pd.merge(df, aggregate_data, on='geo_id')
    
    # Set some common values
    df['NAME'] = df['geo_id'] = df['aggregate_id']
    
    # Drop the extra column
    df = df.drop(['aggregate_id'], axis=1)   
    
    # Determine the columns
    cols_to_keep = list(df.columns.values) 
    cols_to_aggregate = [e for e in cols_to_keep if e not in ('NAME', 'geo_id')]
    
    # Deal with the margin of error
    if 'count_moe' in cols_to_aggregate:
        # Square the Margin of Error
        df['count_moe'] = df['count_moe'] ** 2
    
    # Aggregate (Sum)
    df = df.groupby(['NAME', 'geo_id'])[cols_to_aggregate].sum().reset_index()
    
    # Deal with margin of error
    if 'count_moe' in cols_to_aggregate:
        # Square root the sum of squares
        df['count_moe'] = df['count_moe'] ** .5    
    
    return df[cols_to_keep]

def get_weighted_average_aggregate(df, aggregate_me, var_name, weight_var_name):
    aggregate_data = list()
    for a in aggregate_me:
        aggregate_data.append({'geo_id': a[0], 'aggregate_id': a[1]})
    aggregate_data = pd.DataFrame(aggregate_data)
    
    # Merge it with our data (inner join)
    df = pd.merge(df, aggregate_data, on='geo_id')
    
    # Set some common values
    df['geo_id'] = df['aggregate_id']

    # Aggregate (Sum)
    temp = df.groupby(['geo_id'])[weight_var_name].sum().reset_index().rename(index=str, columns={"weight": "weight_sum"})
    temp = temp.merge(df, on='geo_id')
    # Get the weighted estimate shares
    temp['estimate'] = temp[var_name] * (temp['weight'] / temp['weight_sum'])
    # Sum up the estimates
    temp = temp.groupby(['geo_id'])['estimate'].sum().reset_index()
       
    return temp
    
    
def get_acs_vars(numerator, denominator = False):
    """Translates the numerator and denominator list into a unique list of
    ACS variables that will pulled via the API"""
    # Dictionary of variables we have seen (prevents duplication)
    seen = {}
    acs_vars = ['NAME']
    for n in numerator:
        if n not in seen:
            est_var = n+'E'
            moe_var = n+'M'
            acs_vars.append(est_var)
            acs_vars.append(moe_var)
            seen[n] = 1
    if denominator is not False:
        for d in denominator:
            if d not in seen:
                est_var = d+'E'
                moe_var = d+'M'
                acs_vars.append(est_var)
                acs_vars.append(moe_var)
                seen[d] = 1
    return acs_vars

def get_census_vars(numerator, denominator = False):
    """Translates the numerator and denominator list into a unique list of
    Census 2000 variables that will pulled via the API"""
    # Dictionary of variables we have seen (prevents duplication)
    seen = {}
    census_vars = ['NAME']
    for n in numerator:
        if n not in seen:
            census_vars.append(n)
            seen[n] = 1
    if denominator is not False:
        for d in denominator:
            if d not in seen:
                census_vars.append(d)
                seen[d] = 1
    return census_vars

def get_for_strings(valid_geography):
    """Translate valid geographies into for strings dictionary."""
    for_strings = dict() # {'00': '&for=us:1'}
    for geo_id, row in valid_geography['geographies'].items():
        for_strings[geo_id] = row['for_string']
    return for_strings
    

def get_reliability(df, var_name = 'count', moe_name = 'count_moe'):
    return df[[var_name, moe_name]].apply(get_reliability_stars, axis=1)
    
def get_reliability_stars(d):
    """CGR's rule for creating reliability stars for the estimates"""
    # If there is not MOE return None
    if d[1] == 555555555:
        return None
    # Avoid division by zero errors
    if d[0] == 0:
        return "***"
    # Calculate the MOE/EST
    moe_over_est = d[1] / d[0]
    # Translate the MOE/EST to stars
    if moe_over_est < .2:
        return None
    elif moe_over_est < .35:
        return "*"
    elif moe_over_est < .5:
        return "**"
    else:
        return "***"

def get_theta(row):
    # theta = (LOG(1-Pa)-LOG(1-Pb))/(LOG(upper_bound)-LOG(lower_bound))
    return (row['log_one_minus_Pa'] - row['log_one_minus_Pb']) / (row['log_upper_bound'] - row['log_lower_bound'])

def get_k(row):
    # k = POWER((Pb-Pa)/((1/POWER(lower_bound, theta))-(1/POWER(upper_bound, theta))),(1/theta))
    try:
        k = pow((row['Pb'] - row['Pa'])/((1/pow(row['lower_bound'],row['theta']))-(1/pow(row['upper_bound'], row['theta']))),(1/row['theta']))
    except:
        k = None
    return(k)


def get_median(row):
    # =k*POWER(2,(1/theta))
    if row['k'] is None:
        return None
    else:
        return row['k'] * pow(2, (1/row['theta']))


def find_pb_column(row):
    matched = row == row['Pb']
    matches = row[matched].reset_index()
    return matches['index'][0]

def find_before_measure_class_column(row):
    matched = row == row['before_measure_class']
    matches = row[matched].reset_index()
    return matches['index'][0]

def get_pareto_percentile(row):
    # =k*POWER(2,(1/theta))
    if row['k'] is None:
        return None
    else:
        return row['k'] / pow(1-row['measure'], (1/row['theta'])) 

def pareto_interpolation(aggregate_me, the_vars, aggregates, measure = .5):
    # Get the cummulative sums
    cumsum = aggregate_me.cumsum(axis=1)
    cumfreq = cumsum.div(cumsum[the_vars[-1]], axis=0)
    cumfreq['Pb'] = cumfreq[cumfreq > measure].min(axis=1)
    cumfreq['before_measure_class'] = cumfreq[cumfreq <= measure].max(axis=1)
    cumfreq['variable'] = cumfreq.apply(find_pb_column, axis=1)
    cumfreq['before var'] = cumfreq.apply(find_before_measure_class_column, axis=1)
    cumfreq.reset_index(inplace=True)
    cumsum.reset_index(inplace=True)
    cumsum = pd.merge(cumsum, cumfreq[['geo_id', 'variable', 'before var','Pb']])
    cumsum['begin_of_interval'] = cumsum.lookup(cumfreq.index, cumfreq['before var']) + 1
    cumsum['Pa'] = cumsum['begin_of_interval'].div(cumsum[the_vars[-1]], axis=0)
    cumsum['end_of_interval'] = cumsum.lookup(cumfreq.index, cumfreq['variable'])
    cumsum['lower_bound'] = cumsum['variable'].apply(lambda x: aggregates[x]['lower_bound'])
    cumsum['upper_bound'] = cumsum['variable'].apply(lambda x: aggregates[x]['upper_bound'])
    cumsum['one_minus_Pa'] = 1 - cumsum['Pa']
    cumsum['one_minus_Pb'] = 1 - cumsum['Pb']
    cumsum['log_one_minus_Pa'] = cumsum['one_minus_Pa'].apply(np.log10)
    cumsum['log_one_minus_Pb'] = cumsum['one_minus_Pb'].apply(np.log10)
    cumsum['log_upper_bound'] = cumsum['upper_bound'].apply(np.log10)
    cumsum['log_lower_bound'] = cumsum['lower_bound'].apply(np.log10)

    cumsum['theta'] = cumsum.apply(get_theta, axis=1)
    cumsum['k'] = cumsum.apply(get_k, axis=1)

    if measure == .5:
        cumsum['estimate'] = cumsum.apply(get_median, axis=1)
    else:
        cumsum['measure'] = measure
        cumsum['estimate'] = cumsum.apply(get_pareto_percentile, axis=1)

    cumsum = list(cumsum[['geo_id', 'estimate']].T.to_dict().values())
    cumsum = pd.DataFrame(cumsum)
    return cumsum
        
def validate_geographies(indicator, geographies, geography_ids, include_aggregates = True, pull_all_ci_geographies = False):
    # Get Geographies to pull
    # There can be one of three cases:
    # 1. The user has supplied a list of geographies
    # 2. The user has supplied a dictionary of geographies
    # 3. The user has not predefined the geographies
    
    # Will hold the data that is returned
    geography_names_and_for_strings = dict()
    # Key value pair for the geography id and aggregate id (empty if none)
    geography_names_and_for_strings['aggregate_me'] = list()
    # The geography id, name, and "for string" data
    geography_names_and_for_strings['geographies'] = dict()

    # Connect to the data hub    
    hub = Hub()
    
    # Count of the geographies found
    items_found = 0
    total_items = 0
    
    check_for_aggregates = False
    
    # Case 1. The user has supplied a list of geographies
    if isinstance(geographies, (list,)):
        # Count how many items are in the list
        total_items = len(geographies)
        
        # Create the SQL statement
        sql = "SELECT `CGR_GEO_ID`, `NAME` AS `name`, `CENSUS_API_GEOGRAPHY_STRING` AS `for_string` FROM `CGR_GeographyIndex` WHERE `CGR_GEO_ID` IN ("
        # Add in all the geographies
        for geo in geographies:
            sql = sql + "'" + geo + "', "
        # Drop the last comma and space and close the IN statement
        sql = sql[:-2] + ");"
        # TODO Remove the following line
        check_for_aggregates = True
        
    # Case 2. The user has supplied a dictionary of geographies
    elif isinstance(geographies, (dict,)):
         # Count how many items are in the list
        total_items = len(geographies.keys())
        # Create the SQL statement
        sql = "SELECT `CGR_GEO_ID`, `NAME` AS `name`, `CENSUS_API_GEOGRAPHY_STRING` AS `for_string` FROM `CGR_GeographyIndex` WHERE `CGR_GEO_ID` IN ("
        # Add in all the geographies
        for geo in geographies.keys():
            sql = sql + "'" + geo + "', "
        # Drop the last comma and space and close the IN statement
        sql = sql[:-2] + ");"
        
    # Case 3. The user has not predefined the geographies
    else:
        check_for_aggregates = True
        if pull_all_ci_geographies:
            sql = '''SELECT CGR_GEO_ID, NAME AS `name`, CENSUS_API_GEOGRAPHY_STRING AS `for_string`
            FROM `CGR_GeographyIndex`
            WHERE `CI_GEO` = 1
            AND `CENSUS_API_GEOGRAPHY_STRING` IS NOT NULL;'''
        else:
            # Pull geographies that are for clients that want this indicator plus
            # NYC for Rest of State calculations
            sql = '''SELECT geo.CGR_GEO_ID, geo.NAME AS `name`, geo.CENSUS_API_GEOGRAPHY_STRING AS `for_string`
            FROM (CI_ClientIndicators AS ci
            INNER JOIN CI_ClientGeography AS cg
            ON ci.CI_Client_id = cg.CI_Client_id)
            INNER JOIN CGR_GeographyIndex AS geo
            ON cg.CGR_GEO_ID = geo.CGR_GEO_ID
            WHERE ci.Status="Active"
            GROUP BY ci.CI_Indicator_id, geo.CGR_GEO_ID, geo.NAME, geo.CI_GEO, geo.CENSUS_API_GEOGRAPHY_STRING
            HAVING (ci.CI_Indicator_id="''' + indicator + '''"
            AND geo.CI_GEO=1
            AND geo.CENSUS_API_GEOGRAPHY_STRING IS NOT NULL)
            UNION
            SELECT CGR_GeographyIndex.CGR_GEO_ID, CGR_GeographyIndex.NAME AS `name`, CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING AS `for_string`
            FROM CI_ClientIndicators
            INNER JOIN (CI_ClientGeography INNER JOIN (XWALK_DWGeographyAggregates INNER JOIN CGR_GeographyIndex ON XWALK_DWGeographyAggregates.DW_Geography_id = CGR_GeographyIndex.CGR_GEO_ID) ON CI_ClientGeography.CGR_GEO_ID = XWALK_DWGeographyAggregates.Aggregates_to) ON CI_ClientIndicators.CI_Client_id = CI_ClientGeography.CI_Client_id
            WHERE (CI_ClientIndicators.Status="Active" AND CI_ClientIndicators.CI_Indicator_id="''' + indicator + '''")
            GROUP BY CGR_GeographyIndex.CGR_GEO_ID, CGR_GeographyIndex.NAME, CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING
            HAVING CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING IS NOT NULL
            UNION
            SELECT CGR_GeographyIndex.CGR_GEO_ID, CGR_GeographyIndex.NAME AS `name`, CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING AS `for_string`
            FROM CGR_GeographyIndex
            WHERE CGR_GeographyIndex.CGR_GEO_ID="3651000";'''
   
    #print(geographies)
    
    # Close the hub connection
    
    # Execute the statement 
    q = hub.query(sql)
    
    # Process the results
    for row in q:
        # Convert SQL Alchemy row to dictionary
        row = dict(row)
        # Get the id
        i = row['CGR_GEO_ID']
        # Remove it from the dictionary b/c we don't want it in the final dictionary
        del(row['CGR_GEO_ID'])
        if isinstance(geographies, (dict,)):
            # Swap out the name 
            row['name'] = geographies[i]
        # Add data to final dictionary
        geography_names_and_for_strings['geographies'][i] = row
        # Add to our items found count
        items_found = items_found + 1
    
    # Check to see if all items were found
    if items_found < total_items:
        print('Warning:', str(items_found), 'out of', str(total_items), 'geographies valid')
    
    if check_for_aggregates and include_aggregates:
        # Handle the aggregates 
        sql = '''SELECT CGR_GeographyIndex.CGR_GEO_ID, XWALK_DWGeographyAggregates.Aggregates_to, CGR_GeographyIndex.NAME AS `name`, CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING AS `for_string`
            FROM CI_ClientIndicators
            INNER JOIN (CI_ClientGeography INNER JOIN (XWALK_DWGeographyAggregates INNER JOIN CGR_GeographyIndex ON XWALK_DWGeographyAggregates.DW_Geography_id = CGR_GeographyIndex.CGR_GEO_ID) ON CI_ClientGeography.CGR_GEO_ID = XWALK_DWGeographyAggregates.Aggregates_to) ON CI_ClientIndicators.CI_Client_id = CI_ClientGeography.CI_Client_id
            WHERE (CI_ClientIndicators.Status="Active" AND CI_ClientIndicators.CI_Indicator_id="''' + indicator + '''")
            GROUP BY CGR_GeographyIndex.CGR_GEO_ID,  XWALK_DWGeographyAggregates.Aggregates_to, CGR_GeographyIndex.NAME, CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING
            HAVING CGR_GeographyIndex.CENSUS_API_GEOGRAPHY_STRING IS NOT NULL'''
        q = hub.query(sql)
        
         # Process the results
        for row in q:
            # Convert SQL Alchemy row to dictionary
            row = dict(row)
            # Aggregation tupple
            agg = (row['CGR_GEO_ID'], row['Aggregates_to'])
            geography_names_and_for_strings['aggregate_me'].append(agg)
            del(row['Aggregates_to'])
            # Get the id
            i = row['CGR_GEO_ID']
            # Remove it from the dictionary b/c we don't want it in the final dictionary
            del(row['CGR_GEO_ID'])
            # Add data to final dictionary
            geography_names_and_for_strings['geographies'][i] = row
            
    hub.disconnect()
    return(geography_names_and_for_strings)
    
def combine_dfs(df_a, df_b):
    pd.concat([df_a, df_b], axis=1)
    
def save_to_hub(df, indicator):
    hub = Hub()
    table_name = indicator + '_UPDATE'
    hub.save(df, table_name)

def save_to_excel(df, file_name):
    writer = pd.ExcelWriter(file_name)
    df.to_excel(writer,'Sheet1', index = False)
    writer.save()

    