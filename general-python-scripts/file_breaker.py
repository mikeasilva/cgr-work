#-------------------------------------------------------------------------------
# Name:        File Breaker
# Purpose:     This breaks large text files by character position and saves the
#              output as a .csv file
# Author:      Mike Silva
#
# Created:     30/04/2014
# Copyright:   (c) Mike Silva 2014
# Licence:     GPL
#-------------------------------------------------------------------------------

import pandas as pd

def file_breaker(path, variable_names, starts, ends = False, print_progress = False):

    # This will indicate the row from the input file
    line_number = 0

    # Get the full file length
    file_length = file_len(path)

    # this data frame will hold the parsed data
    df = pd.DataFrame(columns=variable_names)

    # This temporary dictionary will hold the data
    temp_dict = dict()

    # Open the file
    f = open(path, 'r')

    for line in f:
        # Loop through the items
        line_number = line_number + 1
        temp_dict = dict()
        for i in range(0,len(variable_names)):
            # This is the begining character.  Since a Python index begins with
            # zero we have to subtract off one
            begin = starts[i] - 1

            if(ends == False):
                # this is the begining of the next column
                end = starts[i+1] - 1
            else:
                end = ends[i] - 1

            # This is the variable value
            v = line[begin:end]

            # This is the variable's key
            k = variable_names[i]

            # Add this to the temp dictonary
            temp_dict.update({k:v})

        # Append the temp dictonary to the data frame
        df = df.append(temp_dict, ignore_index=True)
        # Print the Progress
        if(print_progress):
            percent_done = round((line_number / file_length)*100,1)
            print ('Line',line_number,'of',file_length,'(',percent_done,'%)')

    # Write the data frame to a file
    df.to_csv(path+'.csv')
    print("Done")


# This fuction gets the number of lines in a text file.  This was found on
# Stack Overflow
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

path = 'M:\FBI\KCRETA00.DAT'
variable_names = ['StateCode',	'Year',	'MonthsReported',	'CityPop',	'CensusPop1',	'CensusPop2',	'CensusPop3',	'AgencyName',	'AgencyState',	'ZipCode',	'JanActualMurder',	'JanActualManslaughter',	'JanActualRapeTotal',	'JanActualRapeByForce',	'JanActualAttemptedRape',	'JanActualRobberyTotal',	'JanActualRobberyWithGun',	'JanActualRobberyWithKnife',	'JanActualRobberyWithOtherWeapon',	'JanActualRobberyWithStrongArm',	'JanActualAssaultTotal',	'JanActualAssaultGun',	'JanActualAssaultKnife',	'JanActualAssaultOther',	'JanActualAssaultHandsFeet',	'JanActualSimpleAssault',	'JanActualBurglaryTotal',	'JanActualBurglaryForcibleEntry',	'JanActualBurglaryNoForcibleEntry',	'JanActualAttemptedBurglary',	'JanActualLarcenyTotal',	'JanActualMotorVehicleTheftTotal',	'JanActualAutoTheft',	'JanActualTruckBusTheft',	'JanActualOtherVehTheft',	'JanActualGrandTotalAllFields',	'JanActualLarcenyUnder50',	'FebActualMurder',	'FebActualManslaughter',	'FebActualRapeTotal',	'FebActualRapeByForce',	'FebActualAttemptedRape',	'FebActualRobberyTotal',	'FebActualRobberyWithGun',	'FebActualRobberyWithKnife',	'FebActualRobberyWithOtherWeapon',	'FebActualRobberyWithStrongArm',	'FebActualAssaultTotal',	'FebActualAssaultGun',	'FebActualAssaultKnife',	'FebActualAssaultOther',	'FebActualAssaultHandsFeet',	'FebActualSimpleAssault',	'FebActualBurglaryTotal',	'FebActualBurglaryForcibleEntry',	'FebActualBurglaryNoForcibleEntry',	'FebActualAttemptedBurglary',	'FebActualLarcenyTotal',	'FebActualMotorVehicleTheftTotal',	'FebActualAutoTheft',	'FebActualTruckBusTheft',	'FebActualOtherVehTheft',	'FebActualGrandTotalAllFields',	'FebActualLarcenyUnder50',	'MarActualMurder',	'MarActualManslaughter',	'MarActualRapeTotal',	'MarActualRapeByForce',	'MarActualAttemptedRape',	'MarActualRobberyTotal',	'MarActualRobberyWithGun',	'MarActualRobberyWithKnife',	'MarActualRobberyWithOtherWeapon',	'MarActualRobberyWithStrongArm',	'MarActualAssaultTotal',	'MarActualAssaultGun',	'MarActualAssaultKnife',	'MarActualAssaultOther',	'MarActualAssaultHandsFeet',	'MarActualSimpleAssault',	'MarActualBurglaryTotal',	'MarActualBurglaryForcibleEntry',	'MarActualBurglaryNoForcibleEntry',	'MarActualAttemptedBurglary',	'MarActualLarcenyTotal',	'MarActualMotorVehicleTheftTotal',	'MarActualAutoTheft',	'MarActualTruckBusTheft',	'MarActualOtherVehTheft',	'MarActualGrandTotalAllFields',	'MarActualLarcenyUnder50',	'AprActualMurder',	'AprActualManslaughter',	'AprActualRapeTotal',	'AprActualRapeByForce',	'AprActualAttemptedRape',	'AprActualRobberyTotal',	'AprActualRobberyWithGun',	'AprActualRobberyWithKnife',	'AprActualRobberyWithOtherWeapon',	'AprActualRobberyWithStrongArm',	'AprActualAssaultTotal',	'AprActualAssaultGun',	'AprActualAssaultKnife',	'AprActualAssaultOther',	'AprActualAssaultHandsFeet',	'AprActualSimpleAssault',	'AprActualBurglaryTotal',	'AprActualBurglaryForcibleEntry',	'AprActualBurglaryNoForcibleEntry',	'AprActualAttemptedBurglary',	'AprActualLarcenyTotal',	'AprActualMotorVehicleTheftTotal',	'AprActualAutoTheft',	'AprActualTruckBusTheft',	'AprActualOtherVehTheft',	'AprActualGrandTotalAllFields',	'AprActualLarcenyUnder50',	'MayActualMurder',	'MayActualManslaughter',	'MayActualRapeTotal',	'MayActualRapeByForce',	'MayActualAttemptedRape',	'MayActualRobberyTotal',	'MayActualRobberyWithGun',	'MayActualRobberyWithKnife',	'MayActualRobberyWithOtherWeapon',	'MayActualRobberyWithStrongArm',	'MayActualAssaultTotal',	'MayActualAssaultGun',	'MayActualAssaultKnife',	'MayActualAssaultOther',	'MayActualAssaultHandsFeet',	'MayActualSimpleAssault',	'MayActualBurglaryTotal',	'MayActualBurglaryForcibleEntry',	'MayActualBurglaryNoForcibleEntry',	'MayActualAttemptedBurglary',	'MayActualLarcenyTotal',	'MayActualMotorVehicleTheftTotal',	'MayActualAutoTheft',	'MayActualTruckBusTheft',	'MayActualOtherVehTheft',	'MayActualGrandTotalAllFields',	'MayActualLarcenyUnder50',	'JunActualMurder',	'JunActualManslaughter',	'JunActualRapeTotal',	'JunActualRapeByForce',	'JunActualAttemptedRape',	'JunActualRobberyTotal',	'JunActualRobberyWithGun',	'JunActualRobberyWithKnife',	'JunActualRobberyWithOtherWeapon',	'JunActualRobberyWithStrongArm',	'JunActualAssaultTotal',	'JunActualAssaultGun',	'JunActualAssaultKnife',	'JunActualAssaultOther',	'JunActualAssaultHandsFeet',	'JunActualSimpleAssault',	'JunActualBurglaryTotal',	'JunActualBurglaryForcibleEntry',	'JunActualBurglaryNoForcibleEntry',	'JunActualAttemptedBurglary',	'JunActualLarcenyTotal',	'JunActualMotorVehicleTheftTotal',	'JunActualAutoTheft',	'JunActualTruckBusTheft',	'JunActualOtherVehTheft',	'JunActualGrandTotalAllFields',	'JunActualLarcenyUnder50',	'JulActualMurder',	'JulActualManslaughter',	'JulActualRapeTotal',	'JulActualRapeByForce',	'JulActualAttemptedRape',	'JulActualRobberyTotal',	'JulActualRobberyWithGun',	'JulActualRobberyWithKnife',	'JulActualRobberyWithOtherWeapon',	'JulActualRobberyWithStrongArm',	'JulActualAssaultTotal',	'JulActualAssaultGun',	'JulActualAssaultKnife',	'JulActualAssaultOther',	'JulActualAssaultHandsFeet',	'JulActualSimpleAssault',	'JulActualBurglaryTotal',	'JulActualBurglaryForcibleEntry',	'JulActualBurglaryNoForcibleEntry',	'JulActualAttemptedBurglary',	'JulActualLarcenyTotal',	'JulActualMotorVehicleTheftTotal',	'JulActualAutoTheft',	'JulActualTruckBusTheft',	'JulActualOtherVehTheft',	'JulActualGrandTotalAllFields',	'JulActualLarcenyUnder50',	'AugActualMurder',	'AugActualManslaughter',	'AugActualRapeTotal',	'AugActualRapeByForce',	'AugActualAttemptedRape',	'AugActualRobberyTotal',	'AugActualRobberyWithGun',	'AugActualRobberyWithKnife',	'AugActualRobberyWithOtherWeapon',	'AugActualRobberyWithStrongArm',	'AugActualAssaultTotal',	'AugActualAssaultGun',	'AugActualAssaultKnife',	'AugActualAssaultOther',	'AugActualAssaultHandsFeet',	'AugActualSimpleAssault',	'AugActualBurglaryTotal',	'AugActualBurglaryForcibleEntry',	'AugActualBurglaryNoForcibleEntry',	'AugActualAttemptedBurglary',	'AugActualLarcenyTotal',	'AugActualMotorVehicleTheftTotal',	'AugActualAutoTheft',	'AugActualTruckBusTheft',	'AugActualOtherVehTheft',	'AugActualGrandTotalAllFields',	'AugActualLarcenyUnder50',	'SepActualMurder',	'SepActualManslaughter',	'SepActualRapeTotal',	'SepActualRapeByForce',	'SepActualAttemptedRape',	'SepActualRobberyTotal',	'SepActualRobberyWithGun',	'SepActualRobberyWithKnife',	'SepActualRobberyWithOtherWeapon',	'SepActualRobberyWithStrongArm',	'SepActualAssaultTotal',	'SepActualAssaultGun',	'SepActualAssaultKnife',	'SepActualAssaultOther',	'SepActualAssaultHandsFeet',	'SepActualSimpleAssault',	'SepActualBurglaryTotal',	'SepActualBurglaryForcibleEntry',	'SepActualBurglaryNoForcibleEntry',	'SepActualAttemptedBurglary',	'SepActualLarcenyTotal',	'SepActualMotorVehicleTheftTotal',	'SepActualAutoTheft',	'SepActualTruckBusTheft',	'SepActualOtherVehTheft',	'SepActualGrandTotalAllFields',	'SepActualLarcenyUnder50',	'OctActualMurder',	'OctActualManslaughter',	'OctActualRapeTotal',	'OctActualRapeByForce',	'OctActualAttemptedRape',	'OctActualRobberyTotal',	'OctActualRobberyWithGun',	'OctActualRobberyWithKnife',	'OctActualRobberyWithOtherWeapon',	'OctActualRobberyWithStrongArm',	'OctActualAssaultTotal',	'OctActualAssaultGun',	'OctActualAssaultKnife',	'OctActualAssaultOther',	'OctActualAssaultHandsFeet',	'OctActualSimpleAssault',	'OctActualBurglaryTotal',	'OctActualBurglaryForcibleEntry',	'OctActualBurglaryNoForcibleEntry',	'OctActualAttemptedBurglary',	'OctActualLarcenyTotal',	'OctActualMotorVehicleTheftTotal',	'OctActualAutoTheft',	'OctActualTruckBusTheft',	'OctActualOtherVehTheft',	'OctActualGrandTotalAllFields',	'OctActualLarcenyUnder50',	'NovActualMurder',	'NovActualManslaughter',	'NovActualRapeTotal',	'NovActualRapeByForce',	'NovActualAttemptedRape',	'NovActualRobberyTotal',	'NovActualRobberyWithGun',	'NovActualRobberyWithKnife',	'NovActualRobberyWithOtherWeapon',	'NovActualRobberyWithStrongArm',	'NovActualAssaultTotal',	'NovActualAssaultGun',	'NovActualAssaultKnife',	'NovActualAssaultOther',	'NovActualAssaultHandsFeet',	'NovActualSimpleAssault',	'NovActualBurglaryTotal',	'NovActualBurglaryForcibleEntry',	'NovActualBurglaryNoForcibleEntry',	'NovActualAttemptedBurglary',	'NovActualLarcenyTotal',	'NovActualMotorVehicleTheftTotal',	'NovActualAutoTheft',	'NovActualTruckBusTheft',	'NovActualOtherVehTheft',	'NovActualGrandTotalAllFields',	'NovActualLarcenyUnder50',	'DecActualMurder',	'DecActualManslaughter',	'DecActualRapeTotal',	'DecActualRapeByForce',	'DecActualAttemptedRape',	'DecActualRobberyTotal',	'DecActualRobberyWithGun',	'DecActualRobberyWithKnife',	'DecActualRobberyWithOtherWeapon',	'DecActualRobberyWithStrongArm',	'DecActualAssaultTotal',	'DecActualAssaultGun',	'DecActualAssaultKnife',	'DecActualAssaultOther',	'DecActualAssaultHandsFeet',	'DecActualSimpleAssault',	'DecActualBurglaryTotal',	'DecActualBurglaryForcibleEntry',	'DecActualBurglaryNoForcibleEntry',	'DecActualAttemptedBurglary',	'DecActualLarcenyTotal',	'DecActualMotorVehicleTheftTotal',	'DecActualAutoTheft',	'DecActualTruckBusTheft',	'DecActualOtherVehTheft',	'DecActualGrandTotalAllFields',	'DecActualLarcenyUnder50']
starts = [2,	14,	42,	45,	90,	99,	108,	121,	145,	271,	463,	468,	473,	478,	483,	488,	493,	498,	503,	508,	513,	518,	523,	528,	533,	538,	543,	548,	553,	558,	563,	568,	573,	578,	583,	588,	593,	1053,	1058,	1063,	1068,	1073,	1078,	1083,	1088,	1093,	1098,	1103,	1108,	1113,	1118,	1123,	1128,	1133,	1138,	1143,	1148,	1153,	1158,	1163,	1168,	1173,	1178,	1183,	1643,	1648,	1653,	1658,	1663,	1668,	1673,	1678,	1683,	1688,	1693,	1698,	1703,	1708,	1713,	1718,	1723,	1728,	1733,	1738,	1743,	1748,	1753,	1758,	1763,	1768,	1773,	2233,	2238,	2243,	2248,	2253,	2258,	2263,	2268,	2273,	2278,	2283,	2288,	2293,	2298,	2303,	2308,	2313,	2318,	2323,	2328,	2333,	2338,	2343,	2348,	2353,	2358,	2363,	2823,	2828,	2833,	2838,	2843,	2848,	2853,	2858,	2863,	2868,	2873,	2878,	2883,	2888,	2893,	2898,	2903,	2908,	2913,	2918,	2923,	2928,	2933,	2938,	2943,	2948,	2953,	3413,	3418,	3423,	3428,	3433,	3438,	3443,	3448,	3453,	3458,	3463,	3468,	3473,	3478,	3483,	3488,	3493,	3498,	3503,	3508,	3513,	3518,	3523,	3528,	3533,	3538,	3543,	4003,	4008,	4013,	4018,	4023,	4028,	4033,	4038,	4043,	4048,	4053,	4058,	4063,	4068,	4073,	4078,	4083,	4088,	4093,	4098,	4103,	4108,	4113,	4118,	4123,	4128,	4133,	4593,	4598,	4603,	4608,	4613,	4618,	4623,	4628,	4633,	4638,	4643,	4648,	4653,	4658,	4663,	4668,	4673,	4678,	4683,	4688,	4693,	4698,	4703,	4708,	4713,	4718,	4723,	5183,	5188,	5193,	5198,	5203,	5208,	5213,	5218,	5223,	5228,	5233,	5238,	5243,	5248,	5253,	5258,	5263,	5268,	5273,	5278,	5283,	5288,	5293,	5298,	5303,	5308,	5313,	5773,	5778,	5783,	5788,	5793,	5798,	5803,	5808,	5813,	5818,	5823,	5828,	5833,	5838,	5843,	5848,	5853,	5858,	5863,	5868,	5873,	5878,	5883,	5888,	5893,	5898,	5903,	6363,	6368,	6373,	6378,	6383,	6388,	6393,	6398,	6403,	6408,	6413,	6418,	6423,	6428,	6433,	6438,	6443,	6448,	6453,	6458,	6463,	6468,	6473,	6478,	6483,	6488,	6493,	6953,	6958,	6963,	6968,	6973,	6978,	6983,	6988,	6993,	6998,	7003,	7008,	7013,	7018,	7023,	7028,	7033,	7038,	7043,	7048,	7053,	7058,	7063,	7068,	7073,	7078,	7083]
ends = [3,	15,	43,	53,	98,	107,	116,	144,	150,	275,	467,	472,	477,	482,	487,	492,	497,	502,	507,	512,	517,	522,	527,	532,	537,	542,	547,	552,	557,	562,	567,	572,	577,	582,	587,	592,	597,	1057,	1062,	1067,	1072,	1077,	1082,	1087,	1092,	1097,	1102,	1107,	1112,	1117,	1122,	1127,	1132,	1137,	1142,	1147,	1152,	1157,	1162,	1167,	1172,	1177,	1182,	1187,	1647,	1652,	1657,	1662,	1667,	1672,	1677,	1682,	1687,	1692,	1697,	1702,	1707,	1712,	1717,	1722,	1727,	1732,	1737,	1742,	1747,	1752,	1757,	1762,	1767,	1772,	1777,	2237,	2242,	2247,	2252,	2257,	2262,	2267,	2272,	2277,	2282,	2287,	2292,	2297,	2302,	2307,	2312,	2317,	2322,	2327,	2332,	2337,	2342,	2347,	2352,	2357,	2362,	2367,	2827,	2832,	2837,	2842,	2847,	2852,	2857,	2862,	2867,	2872,	2877,	2882,	2887,	2892,	2897,	2902,	2907,	2912,	2917,	2922,	2927,	2932,	2937,	2942,	2947,	2952,	2957,	3417,	3422,	3427,	3432,	3437,	3442,	3447,	3452,	3457,	3462,	3467,	3472,	3477,	3482,	3487,	3492,	3497,	3502,	3507,	3512,	3517,	3522,	3527,	3532,	3537,	3542,	3547,	4007,	4012,	4017,	4022,	4027,	4032,	4037,	4042,	4047,	4052,	4057,	4062,	4067,	4072,	4077,	4082,	4087,	4092,	4097,	4102,	4107,	4112,	4117,	4122,	4127,	4132,	4137,	4597,	4602,	4607,	4612,	4617,	4622,	4627,	4632,	4637,	4642,	4647,	4652,	4657,	4662,	4667,	4672,	4677,	4682,	4687,	4692,	4697,	4702,	4707,	4712,	4717,	4722,	4727,	5187,	5192,	5197,	5202,	5207,	5212,	5217,	5222,	5227,	5232,	5237,	5242,	5247,	5252,	5257,	5262,	5267,	5272,	5277,	5282,	5287,	5292,	5297,	5302,	5307,	5312,	5317,	5777,	5782,	5787,	5792,	5797,	5802,	5807,	5812,	5817,	5822,	5827,	5832,	5837,	5842,	5847,	5852,	5857,	5862,	5867,	5872,	5877,	5882,	5887,	5892,	5897,	5902,	5907,	6367,	6372,	6377,	6382,	6387,	6392,	6397,	6402,	6407,	6412,	6417,	6422,	6427,	6432,	6437,	6442,	6447,	6452,	6457,	6462,	6467,	6472,	6477,	6482,	6487,	6492,	6497,	6957,	6962,	6967,	6972,	6977,	6982,	6987,	6992,	6997,	7002,	7007,	7012,	7017,	7022,	7027,	7032,	7037,	7042,	7047,	7052,	7057,	7062,	7067,	7072,	7077,	7082,	7087]
file_breaker(path, variable_names, starts, ends, False)