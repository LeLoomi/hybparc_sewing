# Marker identity and ROI overview
OUT OF DATE!
> This needs to be kept up to date manually! It is recommended to define your setup here and create your config file after.\
_Breaks in tables are meant for grouping only._

## Marker identities
Alignment: IDs are the anchor/alignment IDs for the ROIs. Use X9er IDs\
Electrode: IDs are the identities for the physical electrodes. Use XN\\{9} IDs

| ID | Type | Name |
|---|---|---|
| 19 | Alignment | Central chest |
| 11 | Electrode | eV1 |
| 12 | Electrode | eV2 |
| 13 | Electrode | eV3 |
| 14 | Electrode | eV4 |
| 15 | Electrode | eV5 |
| 16 | Electrode | eV6 |
| - |  |  |
| 29 | Alignment | Right forearm |
| 21 | Electrode | eRed |
| - |  |  |
| 39 | Alignment | Left forearm |
| 31 | Electrode | eYellow |
| - |  |  |
| 49 | Alignment | Left foot |
| 41 | Electrode | eBlack |
| - |  |  |
| 59 | Alignment | Right foot |
| 51 | Electrode | eGreen |


## Regions of interest

| Align ID | Name | Type | Desired IDs | Desc<sup>1</sup> |
|---|---|---|---|---|
| 19 | rV1 | rectangle | 11 | Region for V1 |
| 19 | rV2 | rectangle | 12 | Region for V2 |
| 19 | rV3 | rectangle | 13 | Region for V3 |
| 19 | rV4 | rectangle | 14 | Region for V4 |
| 19 | rV5 | rectangle | 15 | Region for V5 |
| 19 | rV6 | rectangle | 16 | Region for V6 |
| - |  |  |  |  |
| 29 | rRed | circle | 21 | Region for right hand |
| - |  |  |  |  |
| 39 | rYellow | circle | 31 | Region for left hand |
| - |  |  |  |  |
| 49 | rBlack | circle | 41 | Region for right foot |
| - |  |  |  |  |
| 59 | rGreen | circle | 51 | Region for left foot |
