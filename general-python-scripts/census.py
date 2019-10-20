# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 12:07:08 2018

@author: Michael Silva
"""
import datetime
import os
import sys
import requests
import asyncio
import pandas as pd
import numpy as np


class api(object):
    """Pull Census API data."""

    def __init__(self, job_id=None, api_key=None, api_key_file=None):
        """Initialize the Census object.

         Parameters
        ----------
        job_id : string, optional
            an identifier of the job
        api_key : string, optional
            Census API key
        api_key_file : string, optional
            The path to a file containing the API key on the first line

        """
        self.api_data = None

        self.api_endpoint = None

        self.api_key = None
        if api_key is not None:
            self.api_key = api_key
        elif api_key_file is not None:
            f = open(api_key_file, 'r')
            self.api_key = f.readline().strip()
            f.close()
        else:
            self.api_key = os.environ.get('CENSUS_API_KEY')

        self.api_get_string = ''
        self.api_variables = None
        self.cache = dict()
        self.debugging = False

        self.df = None
        
        self.execptions = list()
        self.exception_report_file_name = None
        self.dataset = None
        self.dataset_info = None
        
        self.total_steps = 0
        self.current_step = 0

        self.for_strings = {'00': '&for=us:1'}

        if job_id is None:
            job_id = self._now_()
        self.job_id = job_id

        self.log_file = None

        self.root_url = 'https://api.census.gov/data/'

    def _now_(self, include_time=True):
        """Get the current date/time.

         Parameters
        ----------
        include_time : boolean, optional
            True if you want the time included (default).

        Returns
        -------
        now : string
            The current date with/without the time.

        """
        now = datetime.datetime.now()
        if include_time:
            now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        else:
            now = now.strftime('%Y-%m-%d')
        return now

    def _quit_with_error_(self, error_message):
        """Quit with an error."""
        self.debug_message(error_message)
        print(error_message)
        sys.exit(error_message)

    def chunk_variable_list(self, element_list, n=50):
        """Break a list into a list of lists with n elements.

        This is needed because the API has a 50 variable limit.

        Parameters
        ----------
        element_list : list
            a list of elements to be chunked up.
        n : int, optional
            the maximum number of items in the list.

        Returns
        -------
        chunks : list
            a list of lists containing elements in length equal to or under the
            limit.

        """
        chunks = list()
        if len(element_list) < n:
            chunks.append(element_list)
        else:
            j = range((len(element_list) + n - 1) // n)
            chunks = [element_list[i * n:(i + 1) * n] for i in j]
        return chunks
    
    def close(self):
        """Close up shop."""
        if self.exception_report_file_name is not None:
            print("WARNING: Some requests failed.  See " + self.exception_report_file_name + " for a full report")

    def data_wrangling(self):
        """Wrangle the data.

        Returns
        -------
        df : dataframe
            The pandas data frame.

        """
        self.debug_message('Begining data wrangling')
        chunk_df_cache = dict()
        variable_list = self.api_variables
        self.current_step = 0
        self.total_steps = len(self.cache)
        total_steps = self.total_steps
        for key, item in self.cache.items():
            self.current_step = self.current_step + 1
            self.set_progressbar('Processing', self.current_step, total_steps)
            geo_id = item['geo_id']
            response_json = item['data']
            chunk_df = self.process_df_chunk(response_json, variable_list)
            
            # Only keep valid variables
            keepers = list() 
            columns = list(chunk_df.columns)
            for census_var in variable_list:
                if census_var in columns:
                    keepers.append(census_var)
            chunk_df = chunk_df[keepers]
                
            if geo_id in chunk_df_cache:
                # We already have "seen" this geo id
                # Widen the cached data frame with the additional data
                temp_df = pd.concat([chunk_df_cache[geo_id], chunk_df.copy()], axis=1, sort=False)
                chunk_df_cache[geo_id] = temp_df.copy()
            else:
                # This is the first time we have seen this geography
                # Add in the geography id
                #chunk_df['geo_id'] = geo_id
                chunk_df.loc[:, 'geo_id'] = geo_id
                # Store it in the cache for further processing
                chunk_df_cache[geo_id] = chunk_df.copy()

            
        # We have run through all the wrangling so let's build the 
        # final data frame from the cache
        for key, chunk_df in chunk_df_cache.items():
            if self.df is None:
                self.df = chunk_df.copy()
                final_columns = list(chunk_df.columns)
            else:
                chunk_df = chunk_df[final_columns]
                self.df = self.df.append(chunk_df.copy(), ignore_index=True, sort=False)
        self.df = self.df.reset_index(drop=True)
        self.debug_message('Data wrangling done')
        return self.df
        
    def debug(self):
        """Enable debug mode."""
        self.debugging = True
        self.write_to_log_file('Debug mode started')
        return self

    def debug_message(self, message):
        """Write a message to log if debug mode enabled."""
        if self.debugging:
            self.write_to_log_file(message)

    def fetch(self, url, ids):
        """Fetch data from a url."""
        self.debug_message('fetch('+url+') called')
        self.current_step = self.current_step + 1
        total_steps = self.total_steps
        self.set_progressbar('Downloading', self.current_step, total_steps)
        response = requests.get(url)
        try:
            response_json = response.json()
            r = response_json.copy()
            if url in self.exceptions:
                self.exceptions.remove(url)
        except:
            if url not in self.exceptions:
                self.exceptions.append(url)
            r = None
            self.debug_message('FAILED: (' + url + ') '+ response.text)
            
        return (url, r)

    async def fetch_all(self, urls, ids):
        """Fetch all urls asynchronously."""
        self.debug_message('fetch_all() called')
        self.total_steps = len(urls)
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(None, self.fetch, url, ids) for url in urls]
        for response in await asyncio.gather(*futures):
           self.response_to_cache(response, ids)

    def get_data(self, asynchronous=True, quiet_mode=False):
        """Pull data wrapper."""
        self.debug_message('get_data() called')
        if asynchronous:
            return self.get_data_asynchronously(quiet_mode)
        else:
            return self.get_data_synchronously(quiet_mode)

    def get_data_asynchronously(self, quiet_mode=False):
        """Get the data from the API asynchronously."""
        self.debug_message('get_data_asynchronously() called')

        # Check if the API parameters are set
        self.validation_check()

        # Chunk up the variable request
        variable_lists = self.chunk_variable_list(self.api_variables)
        # Build url request list
        api_urls = list()
        api_ids = dict()
        self.debug_message('==================')
        self.debug_message('|| API URL LIST ||')
        self.debug_message('==================')
        for geo_id, for_string in self.for_strings.items():
            for variable_list in variable_lists:
                api_url = self.root_url + self.api_endpoint + '?get='
                for census_var in variable_list:
                    api_url += census_var + ','
                api_url = api_url[:-1]
                final_api_url = api_url + for_string + self.api_get_string + '&key=' + self.api_key
                self.debug_message(final_api_url)
                api_urls.append(final_api_url)
                api_ids[final_api_url] = geo_id
        n = str(len(api_urls))
        print('1st pass for ' + str(n) + ' requests')
        self.debug_message(n + ' URLS to be pulled asynchronously')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.fetch_all(api_urls, api_ids))
        # Try to pull the exceptions
        n = len(self.exceptions)
        if n > 0:
            self.total_steps = n
            self.current_step = 0
            print('2nd pass for ' + str(n) + ' requests')
            self.debug_message('2nd pass for ' + str(n) + ' exceptions')
            loop.run_until_complete(self.fetch_all(self.exceptions, api_ids))
            n = len(self.exceptions)
            if n > 0:
                self.total_steps = n
                self.current_step = 0
                print('3rd pass for ' + str(n) + ' requests')
                #elf.debug_message('3rd pass for ' + str(n) + ' exceptions')
                #loop.run_until_complete(self.fetch_all(self.exceptions, api_ids))
                for final_api_url in self.exceptions:
                    response = self.fetch(final_api_url, api_ids)
                    self.response_to_cache(response, api_ids)
                if len(self.exceptions) > 0:
                    # Exception report
                    self.debug_message('Unable to pull data ' + str(len(self.exceptions)) + ' times')
                    self.save_exceptions(api_ids)
                    self.debug_message('====================')
                    self.debug_message('|| EXCEPTION LIST ||')
                    self.debug_message('====================')
                    i = 0
                    for e in self.exceptions:
                        i = i + 1
                        self.debug_message(str(i) + '. ' + api_ids[e] + ' > ' + e)
        
        self.debug_message('Event Loop Done')
        self.data_wrangling()
        return self.df
    
    def get_data_synchronously(self, quiet_mode=False):
        """Get the data from the API."""
        self.debug_message('get_data_synchronously() called')

        # Check if the API parameters are set
        self.validation_check()

        # Chunk up the variable request
        variable_lists = self.chunk_variable_list(self.api_variables)

        # Make the requests
        self.total_steps = len(self.for_strings) * len(variable_lists)

        ids = dict()
        for geo_id, for_string in self.for_strings.items():
            self.debug_message('Getting data for: ' + str(geo_id))
            for variable_list in variable_lists:
                api_url = self.root_url + self.api_endpoint + '?get='
                for census_var in variable_list:
                    api_url += census_var + ','
                api_url = api_url[:-1]
                final_api_url = api_url + for_string + self.api_get_string + '&key=' + self.api_key
                ids[final_api_url] = geo_id
                
                response = self.fetch(final_api_url, ids)
                self.response_to_cache(response, ids)

        # Try to pull the exceptions
        n = len(self.exceptions)
        if n > 0:
            self.total_steps = n
            self.current_step = 0
            print('2nd Pass for ' + str(n) + '  requests')
            self.debug_message('2nd pass for '+ str(n) + ' exceptions to be pulled synchronously')
            for final_api_url in self.exceptions:
                response = self.fetch(final_api_url, ids)
                self.response_to_cache(response, ids)
            n = len(self.exceptions)
            if n > 0:
                self.total_steps = n
                self.current_step = 0
                print('3rd Pass for ' + str(n) + '  requests')
                self.debug_message('3rd pass for '+ str(n) + ' exceptions to be pulled synchronously')
                for final_api_url in self.exceptions:
                    response = self.fetch(final_api_url, ids)
                    self.response_to_cache(response, ids)
                    
                self.debug_message('Unable to pull data ' + str(len(self.exceptions)) + ' times')
                if len(self.exceptions) > 0:
                    # Exception report
                    self.save_exceptions(ids)
                    self.debug_message('====================')
                    self.debug_message('|| EXCEPTION LIST ||')
                    self.debug_message('====================')
                    i = 0
                    for e in self.exceptions:
                        i = i + 1
                        self.debug_message(str(i) + '. ' + ids[e] + ' > ' + e)
                
        self.data_wrangling()
        return self.df        
        
    def process_df_chunk(self, response_json, variable_list):
        """Process the dataframe chunk."""
        self.debug_message('process_df_chunk() called')
        columns = response_json.pop(0)
        chunk_df = pd.DataFrame(response_json, columns=columns)
        replace = {'-666666666': np.NaN, '-222222222': np.NaN, '-555555555': np.NaN}
        chunk_df.replace(replace, inplace=True)
        # Convert the requested data to numeric
        columns = list(chunk_df.columns.values)
        for census_var in variable_list:
            if census_var in columns:
                #self.debug_message('Converting '+census_var)
                chunk_df[census_var] = chunk_df[census_var].apply(pd.to_numeric, errors='ignore')
        return chunk_df
    
    def reset(self):
        """ Reset API to initial settings """
        self.debug_message('reset() called')
        self.cache = dict()
        self.df = None
        self.total_steps = 0
        self.current_step = 0
        self.exceptions = list()
        return self
    
    def response_to_cache(self, response, ids):
        """Save the API response to the cache."""
        self.debug_message('response_to_cache() called')
        if response[1] != None:
            url = response[0]
            response_json = response[1]
            geo_id = ids[url]
            self.cache[url] = {'data': response_json,
                      'geo_id': geo_id}
        return self
    
    def save_exceptions(self, ids):
        """Save the API failures."""
        self.debug_message('save_exceptions() called')
        # Create file if it doesn't exist
        if self.exception_report_file_name is None:
            file_name = 'API Report/Exception Report ' + self.job_id + '.txt'
            file_name = file_name.replace(':', '.') # Make it safe for windows
            self.exception_report_file_name = file_name
        # Write to the file
        f = open(self.exception_report_file_name, 'a')
        f.write(self.dataset + "\n")
        if self.dataset_info is not None:
            f.write(self.dataset_info + "\n")
        i = 0
        for e in self.exceptions:
            i = i + 1
            f.write(str(i) + '. (CGR GEO ID:' + ids[e] + ') ' + e + "\n")
        f.close()
            
        return self

    def set_api_endpoint(self, api_id):
        """Set the API endpoint."""
        settings = self.settings()
        self.dataset = settings[api_id]['name']
        self.api_endpoint = api_endpoint = settings[api_id]['api_endpoint']
        self.debug_message('API endpoint set to ' + api_endpoint)
        return self
    
    def set_api_get_string(self, api_get_string):
        """Set the API GET string."""
        self.api_get_string = api_get_string
        self.debug_message('API GET string set to '+api_get_string)
        return self

    def set_api_key(self, api_key):
        """Set the API key."""
        self.api_key = api_key
        hidden_api_key = '*' * len(self.api_key)
        self.debug_message('API key set to ' + hidden_api_key)
        return self

    def set_api_variables(self, api_variables):
        """Set the variable to request from the API."""
        self.api_variables = api_variables
        self.debug_message('API Variables Set')
        return self
    
    def set_dataset_info(self, dataset_info):
        """Set info about the dataset."""
        self.dataset_info = dataset_info
        self.debug_message('Dataset Info Set')
        return self

    def set_for_strings(self, for_strings):
        """Set the dictionary of geographies to pull the data for."""
        self.for_strings = for_strings
        self.debug_message('API for strings set to ' + str(for_strings))
        return self

    def set_job_id(self, job_id):
        """Set a unique id for this job."""
        self.job_id = job_id
        self.debug_message('Job id set to ' + job_id)
        return self

    def set_progressbar(self, message, numerator, denominator):
        """Update the progress indicator."""
        percent_complete = int((numerator / denominator) * 100)
        if percent_complete == 100:
            flush = False
            end = '\n'
        else:
            flush = True
            end = ''
        print("\r"+message+": %d%%" % percent_complete, end=end, flush=flush)
        
    def settings(self):
        # Census API Settings
        census_settings = dict()
        
        latest_acs_5_year = 2013.5
        previous_acs_5_year = latest_acs_5_year - 5
        
        latest_acs_1_year = 2017
        
        latest_sahie_year = 2017
        
        # ACS 5 Years
        census_settings[2013.5] = {'api_endpoint': '2017/acs/acs5', 'name': '2013-17 ACS',
                                   'year_text': '2013-17', 'inflation_year': 2017,
                                   'year': 2013.5}
        census_settings[2012.5] = {'api_endpoint': '2016/acs/acs5', 'name': '2012-16 ACS',
                                   'year_text': '2012-16', 'inflation_year': 2016,
                                   'year': 2012.5}
        census_settings[2011.5] = {'api_endpoint': '2015/acs/acs5', 'name': '2011-15 ACS',
                                   'year_text': '2011-15', 'inflation_year': 2015,
                                   'year': 2011.5}
        census_settings[2010.5] = {'api_endpoint': '2010/acs/acs5', 'name': '2010-14 ACS',
                                   'year_text': '2010-14', 'inflation_year': 2010,
                                   'year': 2010.5}
        census_settings[2009.5] = {'api_endpoint': '2013/acs/acs5', 'name': '2009-13 ACS',
                                   'year_text': '2009-13', 'inflation_year': 2013,
                                   'year': 2009.5}
        census_settings[2008.5] = {'api_endpoint': '2012/acs/acs5', 'name': '2008-12 ACS',
                                   'year_text': '2008-12', 'inflation_year': 2012,
                                   'year': 2008.5}
        census_settings[2007.5] = {'api_endpoint': '2011/acs/acs5', 'name': '2007-11 ACS',
                                   'year_text': '2007-11', 'inflation_year': 2011,
                                   'year': 2007.5}
        census_settings[2006.5] = {'api_endpoint': '2010/acs5', 'name': '2006-10 ACS',
                                   'year_text': '2006-10', 'inflation_year': 2010, 
                                   'year': 2006.5} 
        
        # Census 2000
        census_settings['2000-sf1'] = {'api_endpoint': '2000/sf1', 'name': 'Census 2000 SF-1',
                                       'year_text': '2000', 'inflation_year': 1999, 
                                       'year':2000}
        census_settings['2000-sf3'] = {'api_endpoint': '2000/sf3', 'name': 'Census 2000 SF-3',
                                       'year_text': '2000', 'inflation_year': 1999,
                                       'year': 2000}
        # ACS One Years
        census_settings[2018] = {'api_endpoint': '2018/acs/acs1', 'name': '2018 ACS',
                                 'year_text': '2018', 'inflation_year': 2018, 
                                 'year':2018}
        census_settings[2017] = {'api_endpoint': '2017/acs/acs1', 'name': '2017 ACS',
                                 'year_text': '2017', 'inflation_year': 2017,
                                 'year':2017}
        census_settings[2016] = {'api_endpoint': '2016/acs/acs1', 'name': '2016 ACS',
                                 'year_text': '2016', 'inflation_year': 2016,
                                 'year':2016}
        census_settings[2015] = {'api_endpoint': '2015/acs1', 'name': '2015 ACS',
                                 'year_text': '2015', 'inflation_year': 2015,
                                 'year':2015}    
        census_settings[2014] = {'api_endpoint': '2014/acs1', 'name': '2014 ACS',
                                 'year_text': '2014', 'inflation_year': 2014,
                                 'year':2014}
        census_settings[2013] = {'api_endpoint': '2013/acs1', 'name': '2013 ACS',
                                 'year_text': '2013', 'inflation_year': 2013,
                                 'year':2013}       
        
        
        census_settings['2012.5-profile'] = {'api_endpoint': '2016/acs/acs5/profile',
                                             'year_text': '2012-16', 'year':2012.5,
                                             'inflation_year': 2016,}
        census_settings['2007.5-profile'] = {'api_endpoint': '2011/acs/acs5/profile',
                                             'year_text': '2007-11', 'year':2007.5,
                                             'inflation_year': 2011}
        census_settings['2012.5-subject'] = {'api_endpoint': '2016/acs/acs5/subject',
                                             'year_text': '2012-16', 'year':2012.5,
                                             'inflation_year': 2016}
        census_settings['2007.5-subject'] = {'api_endpoint': '2011/acs/acs5/subject',
                                             'year_text': '2007-11', 'year':2007.5,
                                             'inflation_year': 2011}
        # SAHIE
        census_settings['sahie'] = {'api_endpoint': 'timeseries/healthins/sahie',  'name': 'SAHIE',
                                    'earliest_year': 2008, 
                                    'latest_year': latest_sahie_year}
        
        # Latest
        census_settings['latest_acs_5_year'] = census_settings[latest_acs_5_year]
        census_settings['previous_acs_5_year'] = census_settings[previous_acs_5_year]
        census_settings['latest_acs_1_year'] = census_settings[latest_acs_1_year]
        
        # CGR's API Key
        census_settings['api_key'] = 'CENSUS API KEY HERE'
        
        return census_settings

    def validation_check(self):
            """Validate Parameters prior to requesting."""
            self.debug_message('validation_check() called')
            # Check if the API parameters are set
            e = 'ERROR: '
            if self.api_key is None:
                self._quit_with_error_(e + 'Census API key not defined')
            if self.api_endpoint is None:
                self._quit_with_error_(e + 'Census API endpoint not defined')
            if self.api_variables is None:
                self._quit_with_error_(e + 'Census API variables not defined')
            self.debug_message('Passed validation')

    def write_to_log_file(self, message):
        """Write a message to the debug text log."""
        # Create file if it doesn't exist
        if self.log_file is None:
            file_name = 'API Report/Log for Job ' + self.job_id + '.txt'
            file_name = file_name.replace(':', '.') # Make it safe for windows
            self.log_file = file_name
        # Write to the file
        now = self._now_()
        f = open(self.log_file, 'a')
        f.write(now + ' > ' + message + '\n')
        f.close()
        return self        