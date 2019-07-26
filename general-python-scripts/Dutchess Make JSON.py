# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 16:09:42 2019

@author: Michael
"""
import time
start_time = time.time()

import pandas as pd
import json
from hashlib import sha1

data = dict()
keys = set()
coverage = dict()

years_to_average = [2016, 2017, 2018]

files = ["All EMS Responses_V2.5_Jan2016-May2019.xlsx"]

region_name = " Dutchess County"

total_records_processed = 0


def clean_call_type(x):
    if pd.isnull(x):
        return "Unknown"
    x = x.strip()
    if x == "":
        return "Unknown"
    elif x in ["EMS P1", "EMS P2", "EMS P3", "EMS P4", "PIAA P3", "Alarm EMS P3", "Structure Fire", "PIAA P1", "Alarm Fire"]:
        return x
    else:
        return "All Others"


def clean_venue(x):
    if pd.isnull(x):
        return "Unknown"
    x = x.strip()
    if x == "AMENIA":
        return "Town of Amenia"
    elif x == "BEEKMAN":
        return "Town of Beekman"
    elif x == "C/BEACON" :
        return "City of Beacon"
    elif x == "C/POUGHKEEPSIE":
        return "City of Poughkeepsie"
    elif x == "CLERMONT":
        return "Town of Clermont"
    elif x == "CLINTON":
        return "Town of Clinton"
    elif x == "DOVER":
        return "Town of Dover"
    elif x == "EAST FISHKILL":
        return "Town of East Fishkill"
    elif x == "FISHKILL":
        return "Town of Fishkill"
    elif x == "GALLATIN":
        return "Town of Gallatin"
    elif x == "HYDE PARK":
        return "Town of Hyde Park"
    elif x == "LAGRANGE":
        return "Town of Lagrange"
    elif x == "MILAN":
        return "Town of Milan"
    elif x == "NORTH EAST":
        return "Town of North East"
    elif x == "PAWLING":
        return "Town of Pawling"
    elif x == "PINE PLAINS":
        return "Town of Pine Plains"
    elif x == "PLEASANT VALLEY":
        return "Town of Pleasant Valley"
    elif x == "POUGHKEEPSIE":
        return "Town of Poughkeepsie"
    elif x == "RED HOOK":
        return "Town of Red Hook"
    elif x == "RHINEBECK":
        return "Town of Rhinebeck"
    elif x == "STANFORD":
        return "Town of Stanford"
    elif x == "UNION VALE":
        return "Town of Union Vale"
    elif x == "V/FISHKILL":
        return "Village of Fishkill"
    elif x == "V/MILLBROOK":
        return "Village of Millbrook"
    elif x == "V/MILLERTON":
        return "Village of Millerton"
    elif x == "V/PAWLING":
        return "Village of Pawling"
    elif x == "V/RED HOOK":
        return "Village of Red Hook"
    elif x == "V/RHINEBECK":
        return "Village of Rhinebeck"
    elif x == "V/TIVOLI":
        return "Village of Tivoli"
    elif x == "V/WAPPINGERS FALLS":
        return "Village of Wappingers Falls"
    elif x == "WAPPINGER":
        return "Town of Wappinger"
    elif x == "WASHINGTON":
        return "Town of Washington"
    else:
        return "Unknown"


def clean_agency(x):
    if pd.isnull(x):
        return "Unknown"
    x = x.strip()
    if x == "AMEMS":
        return "Amenia EMS"
    elif x == "AMFD":
        return "Amenia Fire"
    elif x == "ARFD":
        return "Arlington Fire"
    elif x == "BEFD":
        return "Beekman Fire"
    elif x == "BNFD":
        return "City of Beacon Fire"
    elif x == "BVAC":
        return "Beacon Volunteer Ambulance Corps"
    elif x == "CARE1EMS":
        return "Other"
    elif x == "CPFD":
        return "Castle Point Fire"
    elif x == "DO EMS":
        return "Dover EMS"
    elif x == "DOFD":
        return "Dover Fire"
    elif x == "ECFD":
        return "East Clinton Fire"
    elif x == "EFEMS":
        return "East Fishkill EMS"
    elif x == "EFFD":
        return "East Fishkill Fire"
    elif x == "EMSTAR" or x == "TRANCARE":
        return "EMStar"
    elif x == "FAFD":
        return "Fairview Fire"
    elif x == "HIFD":
        return "Hillside Fire"
    elif x == "HPFD":
        return "Hyde Park Fire"
    elif x == "IBM EF":
        return "Other"
    elif x == "LAFD":
        return "Lagrange Fire"
    elif x == "MBFD":
        return "Millbrook Fire"
    elif x == "MIFD":
        return "Milan Fire"
    elif x == "MNFD":
        return "Millerton Fire"
    elif x == "MOBILE LF" or x == "MOBILELF":
        return "Mobile Life"
    elif x == "NDP":
        return "NDP"
    elif x == "NEEMS":
        return "Northeast EMS"
    elif x == "OTHERCTY":
        return "Other"
    elif x == "PAFD":
        return "Pawling Fire"
    elif x == "PPFD":
        return "Pine Plains Fire"
    elif x == "PVFD":
        return "Pleasant Valley Fire"
    elif x == "RBFD":
        return "Rhinebeck Fire"
    elif x == "RCFD":
        return "Rhinecliff Fire"
    elif x == "RHFD":
        return "Red Hook Fire"
    elif x == "ROFD":
        return "Roosevelt Fire"
    elif x == "SBFD":
        return "Staatsburg Fire"
    elif x == "STFD":
        return "Stanford Fire"
    elif x == "TIFD":
        return "Tivoli Fire"
    elif x == "UVFD":
        return "Unionvale Fire"
    elif x == "WAFD":
        return "Wappinger Fire"
    elif x == "WAPPINGER":
        return "Wappinger EMS"
    elif x == "WCFD":
        return "West Clinton Fire"
    elif x == "WP EMS":
        return "Other"
    else:
        return "Unknown"


def clean_time_of_day(x):
    if pd.isnull(x):
        return "Unknown"
    elif x < 4:
        return "Overnight 00:00-03:59"
    elif x < 8:
        return "Early Morning 04:00-07:59"
    elif x < 12:
        return "Morning 08:00-11:59"
    elif x < 16:
        return "Afternoon 12:00-15:59"
    elif x < 20:
        return "Evening 16:00-19:59"
    elif x < 24:
        return "Night 20:00-23:59"
    else:
        return "Unknown"


def clean_hour(x):
    if pd.isnull(x):
        return "Unknown"
    if x == 0:
        return "12:00 to 12:59 AM"
    if x == 12:
        return "12:00 to 12:59 PM"
    if x < 13:
        return str(x) + ":00 to " + str(x) + ":59" + " AM"
    elif x < 24:
        x2 = x - 12
        return str(x2) + ":00 to " + str(x2) + ":59" + " PM"
    else:
        return "Unknown"


def clean_season(x):
    if pd.isnull(x):
        return "Unknown"
    elif x in ["December", "January", "February"]:
        return "Winter"
    elif x in ["March", "April", "May"]:
        return "Spring"
    elif x in ["June", "July", "August"]:
        return "Summer"
    elif x in ["September", "October", "November"]:
        return "Fall"
    else:
        return "Unknown"


def add_data(d, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average):
    d["Total"] = d.get("Total", dict())
    d["Total"][year] = d["Total"].get(year, 0) + 1        
    # Month
    d_month = d.get("Month", dict())
    d_month[month_of_year] = d_month.get(month_of_year, dict())
    d["Month"][month_of_year][year] = d_month[month_of_year].get(year, 0) + 1
    # Season
    d_season = d.get("Season", dict())
    d_season[season] = d_season.get(season, dict())
    d["Season"][season][year] = d_season[season].get(year, 0) + 1
    # Day of Week
    d_day = d.get("Day of Week", dict())
    d_day[day_of_week] = d_day.get(day_of_week, dict())
    d["Day of Week"][day_of_week][year] = d_day[day_of_week].get(year, 0) + 1
    # Time of Day
    d_tod = d.get("Time of Day", dict())
    d_tod[time_of_day] = d_tod.get(time_of_day, dict())
    d["Time of Day"][time_of_day][year] = d_tod[time_of_day].get(year, 0) + 1
    # Hour of Day
    d_hour = d.get("Hour", dict())
    d_hour[hour] = d_hour.get(hour, dict())
    d["Hour"][hour][year] = d_hour[hour].get(year, 0) + 1
    # Call Type
    d_call_type = d.get("Call Type", dict())
    d_call_type[call_type] = d_call_type.get(call_type, dict())
    d["Call Type"][call_type][year] = d_call_type[call_type].get(year, 0) + 1
    # Situation Found
    d_sit = d.get("Situation Found", dict())
    d_sit[situation_found] = d_sit.get(situation_found, dict())
    d["Situation Found"][situation_found][year] = d_sit[situation_found].get(year, 0) + 1
    if year in years_to_average:
        d["Total"]["Avg Sum"] = d["Total"].get("Avg Sum", 0) + 1
        d["Month"][month_of_year]["Avg Sum"] = d["Month"][month_of_year].get("Avg Sum", 0) + 1
        d["Season"][season]["Avg Sum"] = d["Season"][season].get("Avg Sum", 0) + 1
        d["Day of Week"][day_of_week]["Avg Sum"] = d["Day of Week"][day_of_week].get("Avg Sum", 0) + 1
        d["Time of Day"][time_of_day]["Avg Sum"] = d["Time of Day"][time_of_day].get("Avg Sum", 0) + 1
        d["Hour"][hour]["Avg Sum"] = d["Hour"][hour].get("Avg Sum", 0) + 1
        d["Call Type"][call_type]["Avg Sum"] = d["Call Type"][call_type].get("Avg Sum", 0) + 1
        d["Situation Found"][situation_found]["Avg Sum"] = d["Situation Found"][situation_found].get("Avg Sum", 0) + 1
        # Create averages
        d["Total"]["Avg"] = int(round(d["Total"]["Avg Sum"] / len(years_to_average), 0))
        d["Month"][month_of_year]["Avg"] = int(round(d["Month"][month_of_year]["Avg Sum"] / len(years_to_average), 0))
        d["Season"][season]["Avg"] = int(round(d["Season"][season]["Avg Sum"] / len(years_to_average), 0))
        d["Day of Week"][day_of_week]["Avg"] = int(round(d["Day of Week"][day_of_week]["Avg Sum"] / len(years_to_average), 0))
        d["Time of Day"][time_of_day]["Avg"] =  int(round(d["Time of Day"][time_of_day]["Avg Sum"] / len(years_to_average), 0))
        d["Hour"][hour]["Avg"] = int(round(d["Hour"][hour]["Avg Sum"] / len(years_to_average), 0))
        d["Call Type"][call_type]["Avg"] = int(round(d["Call Type"][call_type]["Avg Sum"] / len(years_to_average), 0))
        d["Situation Found"][situation_found]["Avg"] = int(round(d["Situation Found"][situation_found]["Avg Sum"] / len(years_to_average), 0))
    return(d)


for f in files:
    print("Reading " + f)
    xl = pd.ExcelFile(f)
    
    for sheet_name in xl.sheet_names:
        if sheet_name != "Legend":
            df = xl.parse(sheet_name, na_values=["", "NULL", -361])
            for i in df.index:
                total_records_processed += 1
                print(str(i + 1) + " of " + str(len(df.index)) + " " + sheet_name + " incidents") 
                # Clean the data
                year = int(df.at[i, "CallDate"].year)
                month_of_year = str(df.at[i, "CallDate"].month_name())
                season = clean_season(month_of_year)
                day_of_week = str(df.at[i, "CallDate"].day_name())
                hour_of_day = int(df.at[i, "CallTime"].hour)
                hour = clean_hour(hour_of_day)
                time_of_day = clean_time_of_day(hour_of_day)
                call_type = clean_call_type(df.at[i, "BaseCallType"])
                situation_found = clean_call_type(df.at[i, "EffectiveCallType"])
                venue_name = clean_venue(df.at[i, "VenueName"])
                # Add in coverage
                cy = coverage.get(year, set())
                cy.add(month_of_year)
                coverage[year] = cy
                
                incident = data.get("Incident", dict())
                venue = data.get("Venue", dict())
                agency = data.get("Agency", dict())
                
                # Check for new incident
                if df.at[i, "CallID"] not in keys:
                    # Add the incident id
                    keys.add(df.at[i, "CallID"])
                    # Add the incident record
                    incident[str(df.at[i, "CallID"])] = {
                        "CallNumber": str(df.at[i, "CallNumber"]),
                        "CallDate": str(df.at[i, "CallDate"]),
                        "CallTime": str(df.at[i, "CallTime"]),
                        "DayOfWeek": df.at[i, "DayOfWeek"],
                        "VenueName": venue_name,
                        "EMS_ORI": df.at[i, "EMS_ORI"],
                        "CallLocation": df.at[i, "CallLocation"],
                        "LatitudeY": df.at[i, "LatitudeY"],
                        "LongitudeX": df.at[i, "LongitudeX"],
                        "BaseCallType": call_type,
                        "DispatchedEMSAgencies": df.at[i, "DispatchedEMSAgencies"],
                        "EffectiveCallType": situation_found,
                        "RespondingEMSAgencies": df.at[i, "RespondingEMSAgencies"],
                        "TransportingEMSAgencies": df.at[i, "TransportingEMSAgencies"],
                        "TransportDestination": df.at[i, "TransportDestination"],
                        "TransportingUnitInServiceTime": df.at[i, "TransportingUnitInServiceTime"],
                        "TransportingUnitAtSceneTime": df.at[i, "TransportingUnitAtSceneTime"]
                        }
                    # Add the venue record
                    v = venue.get(venue_name, {
                            "Total": dict(), 
                            "Month": dict(), 
                            "Season": dict(), 
                            "Day of Week": dict(), 
                            "Time of Day": dict(), 
                            "Hour": dict(), 
                            "Call Type": dict(), 
                            "Situation Found": dict(), 
                            "Dispatched": dict(), 
                            "Responded": dict(), 
                            "Transported": dict()
                            })
                    # Add in the region record
                    v_region = venue.get(region_name, {
                            "Total": dict(), 
                            "Month": dict(), 
                            "Season": dict(), 
                            "Day of Week": dict(), 
                            "Time of Day": dict(), 
                            "Hour": dict(), 
                            "Call Type": dict(), 
                            "Situation Found": dict(), 
                            "Dispatched": dict(), 
                            "Responded": dict(), 
                            "Transported": dict()
                            })
                    venue[venue_name] = add_data(v, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
                    venue[region_name] = add_data(v_region, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
                    
                    
                # Add in the Agency data
                # Dispatched
                if pd.isnull(df.at[i, "DispatchedEMSAgencies"]):
                    dispatched_agency_string = ""
                else:
                    dispatched_agency_string = df.at[i, "DispatchedEMSAgencies"]
                if not pd.isnull(df.at[i, "DispatchedOther"]):
                    dispatched_agency_string = dispatched_agency_string + ", " + (df.at[i, "DispatchedOther"])
                if len(dispatched_agency_string) > 0:
                    for dispatched_agency in (da for da in dispatched_agency_string.split(",")):
                        agency_name = clean_agency(dispatched_agency)
                        agency_key = "Dispatch-"+ agency_name + venue_name + str(df.at[i, "CallID"])
                        if agency_key not in keys:                        
                            keys.add(agency_key)
                            agency[agency_name] = agency.get(agency_name, dict())
                            a_dis = agency[agency_name].get("Dispatched", {
                                    "Total": dict(),
                                    "Month": dict(),
                                    "Season": dict(),
                                    "Day of Week": dict(),
                                    "Time of Day": dict(),
                                    "Hour": dict(),
                                    "Call Type": dict(),
                                    "Situation Found": dict(),
                                    "Venue": dict()
                                    })
                            agency_d = add_data(a_dis, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
                            agency_d["Venue"][venue_name] = agency_d["Venue"].get(venue_name, dict())
                            agency_d["Venue"][venue_name][year] = agency_d["Venue"][venue_name].get(year, 0) + 1
                            agency_d["Venue"][region_name] = agency_d["Venue"].get(region_name, dict())
                            agency_d["Venue"][region_name][year] = agency_d["Venue"][region_name].get(year, 0) + 1
                            if year in years_to_average:
                                agency_d["Venue"][venue_name]["Avg Sum"] = agency_d["Venue"][venue_name].get("Avg Sum", 0) + 1
                                agency_d["Venue"][venue_name]["Avg"] = int(round(agency_d["Venue"][venue_name]["Avg Sum"] / len(years_to_average), 0))
                                agency_d["Venue"][region_name]["Avg Sum"] = agency_d["Venue"][region_name].get("Avg Sum", 0) + 1
                                agency_d["Venue"][region_name]["Avg"] = int(round(agency_d["Venue"][region_name]["Avg Sum"] / len(years_to_average), 0))
                            agency[agency_name]["Dispatched"] = agency_d
                            venue[venue_name]["Dispatched"][agency_name] = venue[venue_name]["Dispatched"].get(agency_name, dict())
                            venue[venue_name]["Dispatched"][agency_name][year] = venue[venue_name]["Dispatched"][agency_name].get(year, 0) + 1
                            venue[region_name]["Dispatched"][agency_name] = venue[region_name]["Dispatched"].get(agency_name, dict())
                            venue[region_name]["Dispatched"][agency_name][year] = venue[region_name]["Dispatched"][agency_name].get(year, 0) + 1
                            if year in years_to_average:
                                venue[venue_name]["Dispatched"][agency_name]["Avg Sum"] = venue[venue_name]["Dispatched"][agency_name].get("Avg Sum", 0) + 1
                                venue[venue_name]["Dispatched"][agency_name]["Avg"] = int(round(venue[venue_name]["Dispatched"][agency_name]["Avg Sum"] / len(years_to_average), 0))
                                venue[region_name]["Dispatched"][agency_name]["Avg Sum"] = venue[region_name]["Dispatched"][agency_name].get("Avg Sum", 0) + 1
                                venue[region_name]["Dispatched"][agency_name]["Avg"] = int(round(venue[region_name]["Dispatched"][agency_name]["Avg Sum"] / len(years_to_average), 0))
                # Responded
                if pd.isnull(df.at[i, "RespondingEMSAgencies"]):
                    responded_agency_string = ""
                else:
                    responded_agency_string = df.at[i, "RespondingEMSAgencies"]
                if not pd.isnull(df.at[i, "RespondedOther"]):
                    responded_agency_string = responded_agency_string + ", " + (df.at[i, "RespondedOther"])
                if len(responded_agency_string) > 0:
                    for responded_agency in (ra for ra in responded_agency_string.split(",")):
                        agency_name = clean_agency(responded_agency)
                        agency_key = "Responded-" + agency_name + venue_name + str(df.at[i, "CallID"])
                        if agency_key not in keys:
                            keys.add(agency_key)
                            agency[agency_name] = agency.get(agency_name, dict())
                            a_res = agency[agency_name].get("Responded", {
                                    "Total": dict(),
                                    "Month": dict(),
                                    "Season": dict(),
                                    "Day of Week": dict(),
                                    "Time of Day": dict(),
                                    "Hour": dict(),
                                    "Call Type": dict(),
                                    "Situation Found": dict(),
                                    "Venue": dict()
                                    })
                            agency_r = add_data(a_res, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
                            agency_r["Venue"][venue_name] = agency_r["Venue"].get(venue_name, dict())
                            agency_r["Venue"][venue_name][year] = agency_r["Venue"][venue_name].get(year, 0) + 1
                            agency_r["Venue"][region_name] = agency_r["Venue"].get(region_name, dict())
                            agency_r["Venue"][region_name][year] = agency_r["Venue"][region_name].get(year, 0) + 1
                            if year in years_to_average:
                                agency_r["Venue"][venue_name]["Avg Sum"] = agency_r["Venue"][venue_name].get("Avg Sum", 0) + 1
                                agency_r["Venue"][venue_name]["Avg"] = int(round(agency_r["Venue"][venue_name]["Avg Sum"] / len(years_to_average), 0))
                                agency_r["Venue"][region_name]["Avg Sum"] = agency_r["Venue"][region_name].get("Avg Sum", 0) + 1
                                agency_r["Venue"][region_name]["Avg"] = int(round(agency_r["Venue"][region_name]["Avg Sum"] / len(years_to_average), 0))
                            agency[agency_name]["Responded"] = agency_r
                            venue[venue_name]["Responded"][agency_name] = venue[venue_name]["Responded"].get(agency_name, dict())
                            venue[venue_name]["Responded"][agency_name][year] = venue[venue_name]["Responded"][agency_name].get(year, 0) + 1
                            venue[region_name]["Responded"][agency_name] = venue[region_name]["Responded"].get(agency_name, dict())
                            venue[region_name]["Responded"][agency_name][year] = venue[region_name]["Responded"][agency_name].get(year, 0) + 1
                            if year in years_to_average:
                                venue[venue_name]["Responded"][agency_name]["Avg Sum"] = venue[venue_name]["Responded"][agency_name].get("Avg Sum", 0) + 1
                                venue[venue_name]["Responded"][agency_name]["Avg"] = int(round(venue[venue_name]["Responded"][agency_name]["Avg Sum"] / len(years_to_average), 0))
                                venue[region_name]["Responded"][agency_name]["Avg Sum"] = venue[region_name]["Responded"][agency_name].get("Avg Sum", 0) + 1
                                venue[region_name]["Responded"][agency_name]["Avg"] = int(round(venue[region_name]["Responded"][agency_name]["Avg Sum"] / len(years_to_average), 0))
                # Transported
                if pd.isnull(df.at[i, "TransportingEMSAgencies"]):
                    transported_agency_string = ""
                else:
                    transported_agency_string = df.at[i, "TransportingEMSAgencies"]
                
                if len(transported_agency_string) > 0:
                    for transported_agency in (ta for ta in transported_agency_string.split(",")):
                        agency_name = clean_agency(transported_agency)
                        agency_key = "Transported-"+ agency_name + venue_name + str(df.at[i, "CallID"])
                        if agency_key not in keys:
                            keys.add(agency_key)
                            agency[agency_name] = agency.get(agency_name, dict())
                            a_tra = agency[agency_name].get("Transported", {
                                    "Total": dict(),
                                    "Month": dict(),
                                    "Season": dict(),
                                    "Day of Week": dict(),
                                    "Time of Day": dict(),
                                    "Hour": dict(),
                                    "Call Type": dict(),
                                    "Situation Found": dict(),
                                    "Venue": dict()
                                    })
                            agency_t = add_data(a_tra, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
                            agency_t["Venue"][venue_name] = agency_t["Venue"].get(venue_name, dict())
                            agency_t["Venue"][venue_name][year] = agency_t["Venue"][venue_name].get(year, 0) + 1
                            agency_t["Venue"][region_name] = agency_t["Venue"].get(region_name, dict())
                            agency_t["Venue"][region_name][year] = agency_t["Venue"][region_name].get(year, 0) + 1
                            if year in years_to_average:
                                agency_t["Venue"][venue_name]["Avg Sum"] = agency_t["Venue"][venue_name].get("Avg Sum", 0) + 1
                                agency_t["Venue"][venue_name]["Avg"] = int(round(agency_t["Venue"][venue_name]["Avg Sum"] / len(years_to_average), 0))
                                agency_t["Venue"][region_name]["Avg Sum"] = agency_t["Venue"][region_name].get("Avg Sum", 0) + 1
                                agency_t["Venue"][region_name]["Avg"] = int(round(agency_t["Venue"][region_name]["Avg Sum"] / len(years_to_average), 0))
                            agency[agency_name]["Transported"] = agency_t
                            venue[venue_name]["Transported"][agency_name] = venue[venue_name]["Transported"].get(agency_name, dict())
                            venue[venue_name]["Transported"][agency_name][year] = venue[venue_name]["Transported"][agency_name].get(year, 0) + 1
                            venue[region_name]["Transported"][agency_name] = venue[region_name]["Transported"].get(agency_name, dict())
                            venue[region_name]["Transported"][agency_name][year] = venue[region_name]["Transported"][agency_name].get(year, 0) + 1
                            if year in years_to_average:
                                venue[venue_name]["Transported"][agency_name]["Avg Sum"] = venue[venue_name]["Transported"][agency_name].get("Avg Sum", 0) + 1
                                venue[venue_name]["Transported"][agency_name]["Avg"] = int(round(venue[venue_name]["Transported"][agency_name]["Avg Sum"] / len(years_to_average), 0))
                                venue[region_name]["Transported"][agency_name]["Avg Sum"] = venue[region_name]["Transported"][agency_name].get("Avg Sum", 0) + 1
                                venue[region_name]["Transported"][agency_name]["Avg"] = int(round(venue[region_name]["Transported"][agency_name]["Avg Sum"] / len(years_to_average), 0))
                # Response Times
                if not pd.isnull(df.at[i, "TransportingUnitAtSceneTime"]):
                    for at_scene_time in df.at[i, "TransportingUnitAtSceneTime"].strip().rstrip(',').split(","):
                        at_scene_key = "At Scene-"+ at_scene_time + str(df.at[i, "CallID"])
                        if at_scene_key not in keys:
                            keys.add(at_scene_key)
                            venue[venue_name]["At Scene Response Time"] = venue[venue_name].get("At Scene Response Time", {"0 to 20 Mins": {
                                "Total": dict(), 
                                "Month": dict(), 
                                "Season": dict(), 
                                "Day of Week": dict(), 
                                "Time of Day": dict(), 
                                "Hour": dict(), 
                                "Call Type": dict(), 
                                "Situation Found": dict(), 
                                "Dispatched": dict(), 
                                "Responded": dict(), 
                                "Transported": dict()
                            }, "Over 20 Mins": {
                                "Total": dict(), 
                                "Month": dict(), 
                                "Season": dict(), 
                                "Day of Week": dict(), 
                                "Time of Day": dict(), 
                                "Hour": dict(), 
                                "Call Type": dict(), 
                                "Situation Found": dict(), 
                                "Dispatched": dict(), 
                                "Responded": dict(), 
                                "Transported": dict()
                            }})
                            venue[region_name]["At Scene Response Time"] = venue[region_name].get("At Scene Response Time", {"0 to 20 Mins": {
                                "Total": dict(), 
                                "Month": dict(), 
                                "Season": dict(), 
                                "Day of Week": dict(), 
                                "Time of Day": dict(), 
                                "Hour": dict(), 
                                "Call Type": dict(), 
                                "Situation Found": dict(), 
                                "Dispatched": dict(), 
                                "Responded": dict(), 
                                "Transported": dict()
                            }, "Over 20 Mins": {
                                "Total": dict(), 
                                "Month": dict(), 
                                "Season": dict(), 
                                "Day of Week": dict(), 
                                "Time of Day": dict(), 
                                "Hour": dict(), 
                                "Call Type": dict(), 
                                "Situation Found": dict(), 
                                "Dispatched": dict(), 
                                "Responded": dict(), 
                                "Transported": dict()
                            }})
                            # Example: (7171) 70.13 Min
                            at_scene_time = float(at_scene_time.split(")")[1].split("Min")[0].strip())
                            if at_scene_time > 20:
                                r_ast = venue[region_name]["At Scene Response Time"]["Over 20 Mins"]
                                v_ast = venue[venue_name]["At Scene Response Time"]["Over 20 Mins"]
                            else:
                                r_ast = venue[region_name]["At Scene Response Time"]["0 to 20 Mins"]
                                v_ast = venue[venue_name]["At Scene Response Time"]["0 to 20 Mins"]
                            venue_ast = add_data(v_ast, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
                            region_ast = add_data(r_ast, year, month_of_year, season, day_of_week, time_of_day, hour, call_type, situation_found, years_to_average)
      
                data = {"Agency": agency, "Incident": incident, "Venue": venue} 


print(str(total_records_processed)+ ' Records Processed in %s seconds' % round((time.time() - start_time), 1))

print("Saving data to JSON files")
# Create countywide data
hash_object = sha1(str(agency).encode())
agency_hash = hash_object.hexdigest()
hash_object = sha1(str(incident).encode())
incident_hash = hash_object.hexdigest()
hash_object = sha1(str(venue).encode())
venue_hash = hash_object.hexdigest()
hash_object = sha1(str(data).encode())
data_hash = hash_object.hexdigest()
with open('agency_' + agency_hash + '.json', 'w') as fp:
    fp.writelines("var agency = " + str(json.dumps(agency)) + ";")
with open('venue_' + venue_hash + '.json', 'w') as fp:
    fp.writelines("var venue = " + str(json.dumps(venue)) + ";")
#with open('incident_' + incident_hash + '.json', 'w') as fp:
#    fp.writelines("var incident = " + str(json.dumps(incident)) + ";")
#with open('data_' + data_hash + '.json', 'w') as fp:
#    fp.writelines("var data = " + str(json.dumps(data)) + ";")