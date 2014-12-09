* need to save as XLS v. 4 or earlier.
GET  translate file ='G:\0ngoing Projects\Econ Data\Employment CES\Finger Lakes Region CES nonSA.txt'
          /type = tab /fieldnames
          /map. 
* sort cases first in year then month order.
SORT cases by year month.
* next command creates year & month in order.
date y 1970 m 1.
* just remember that while you can have the actual year in a variable in the file, this year range can't pass 1999.
TSET MXNEWVARS=1000.
X11ARIMA flrtot flrman flrtwu flrfin flrehs flroth flrnmc flrtra flrinf flrpbs flrlei flrgov
 / title 'TEST non ag employment'/
   format = tables (1) /
   print = analysis /
   plots = none /
   save = pred saf /
   noextremetc.
* sas_1 is the "seasonally adjusted series"; saf_1 is "seasonal adjustment factors".
COMPUTE flrtot@=sas_1.
COMPUTE flrman@=sas_2.
COMPUTE flrtwu@=sas_3.
COMPUTE flrfin@=sas_4.
COMPUTE flrehs@=sas_5.
COMPUTE flroth@=sas_6.
COMPUTE flrnmc@=sas_7.
COMPUTE flrtra@=sas_8.
COMPUTE flrinf@=sas_9.
COMPUTE flrpbs@=sas_10.
COMPUTE flrlei@=sas_11.
COMPUTE flrgov@=sas_12.
COMPUTE flrtotsf=saf_1.
COMPUTE flrmansf=saf_2.
COMPUTE flrtwusf=saf_3.
COMPUTE flrfinsf=saf_4.
COMPUTE flrehssf=saf_5.
COMPUTE flrothsf=saf_6.
COMPUTE flrnmcsf=saf_7.
COMPUTE flrtrasf=saf_8.
COMPUTE flrinfsf=saf_9.
COMPUTE flrpbssf=saf_10.
COMPUTE flrleisf=saf_11.
COMPUTE flrgovsf=saf_12.
LIST year month flrtot flrtot@ flrman flrman@ flrtwu flrtwu@ flrfin flrfin@ flrehs flrehs@ flroth flroth@ flrnmc flrnmc@ flrtra flrtra@ flrinf flrinf@ flrpbs flrpbs@ flrlei flrlei@ flrgov flrgov@ 

* This saves the big file so you can look at all the data

SAVE translate outfile ='G:\0ngoing Projects\Econ Data\Employment CES\Finger Lakes Region CES SA.xls'
          /type = XLS
          /keep = year month flrtot@ flrman@ flrtwu@ flrfin@ flrehs@ flroth@ flrnmc@ flrtra@ flrinf@ flrpbs@ flrlei@ flrgov@ 
          /fieldnames 
          / replace
          / map.