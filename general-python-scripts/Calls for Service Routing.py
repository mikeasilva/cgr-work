# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 12:19:18 2018

@author: Michael
"""
import osmnx as ox
import networkx as nx
import pandas as pd
import os    

filename='dutchess_network.graphml'
root = 'G:/2018 Projects/827-NE Dutchess County Ambulance/Viz/'

def get_total_length(route, G):
    i = 0
    total_length = 0
    for r in route:
        if i > 0:
            edge = G.get_edge_data(route[i], route[i-1])
            try:
                # Meters to Miles conversion
                edge_length = edge[0]['length'] * 0.00062137   
            except:
                edge_length = 0
            total_length = total_length + edge_length
        i = i + 1
    return(total_length)
    
print('Getting road network')

if os.path.isfile(root+'data/'+filename):
    # Read in the file
    G = ox.load_graphml(root+'data/'+filename)
else:
    # Create file since it doesn't exist
    ox.config(use_cache=True, log_console=False)
    G = ox.graph_from_place('Dutchess County, New York, USA', network_type='drive')
    ox.save_graphml(G, filename=filename)
    
stations = pd.read_excel(root+'Drive Distance Data.xlsx', 'Stations')
events = pd.read_excel(root+'Drive Distance Data.xlsx', 'Events')
length_data = list()

for index, row in stations.iterrows():
    station_name = row['Station']
    station = (row['Lat'], row['Lon'])
    station_node= ox.get_nearest_node(G, station)
    for index, e in events.iterrows():
        percent_complete = station_name + ' ' + str(int(index / (events.shape[0]-1) * 100)) + '% complete'
        print(percent_complete, end='')
        print('\r', end='')
        event = (e['Lat'], e['Lon'])
        event_node = ox.get_nearest_node(G, event)
        route = nx.shortest_path(G, station_node, event_node)
        total_length = get_total_length(route, G)
        length_data.append({'Lat':e['Lat'], 'Lon':e['Lon'], 'Station':station_name, 'Distance':total_length})
        
df = pd.DataFrame(length_data)

#f = df.pivot(index=['Lat', 'Lon'], columns='Station', values='Distance')

writer = pd.ExcelWriter('distances.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()
