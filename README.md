This is a simple draft trade chart I developed using draft pick performance values determined by Massey & Thaler in "The Loser's Curse". 

The chart has a toggleable function between trade up and regular trade. In trade up, you are targetting one specific player, and that factors into the calculation. Differently, in regular trade only picks' values are taken into account. 

To use the trade chart, simply select the mode you want and change the contents in the evaluate_trade function call accordingly. Currently, it is set to the Jaguars-Browns blcokbuster trade in the 2025 NFL draft. Travis Hunter's WAR value is an average of the NFL's top 5 CBs and WRs WAR value.

For this model to actually be used, WAR values would need to be calculated or found (and changed accordingly in both cases). Mean and deviation in WAR values for positions come from "PFF WAR: Modeling Player Value in American Football".