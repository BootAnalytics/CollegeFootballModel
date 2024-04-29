My College Football "Performance Ratings" use box score stats to measure team performance.
I use an Elo Model (inspired by chess rankings) to calculate how each team "uses" different stats to win (or lose) games and adjust for opponent.

I uses a statsmodels.OLS regression to convert expected performance of each stat to the expected margin of victory against a given opponent.
In the image below, we can measure the "advantage" the offense has over the opponent's defense in determining who will win the game.

![image](https://github.com/BootAnalytics/CollegeFootballModel/assets/125611355/12f4f7b8-5061-4445-b19f-b03e0e34eae9)

I am able to calculate an expected margin against an "average" opponent, using the average Elo rating for each stat category.

![image](https://github.com/BootAnalytics/CollegeFootballModel/assets/125611355/a5d16071-10a7-422e-ab26-4a8e19ec7a73)

Due to the way the stats and expected margin of victory are calcuated, there's a non-linear relationship between teams (but it is near linear), so the expected margin for a given matchup will differ from the difference in margins against "an average opponent" show in the full rankings.

Work in Progress:
For 2024, I plan to include "Impact Players" to the above head-to-head matchup charts. Below is the impact of "passers" (QBs, excluding their rushing stats).

This is determined by first, looking at how the team should perform (statsmodels.Logit regression) if the team had an average offense.
Then, I calculate what kind of scoring impact (measured in expected TDs) the QB *should* have on the game.
Finally, I take the initial expected performance of the team (given an average offense) and recalculate the team's chance to win considering the QB's passing performance.
<img width="714" alt="image" src="https://github.com/BootAnalytics/CollegeFootballModel/assets/125611355/a1751b81-92c1-42b6-ae87-52eb56ca88dd">

As seen in the image above, there are two key stats for passers: TDs Added and ValueAdded
A QB that has the best defense, playing against a bad opponent, may throw for 5 TDs, but have a low ValueAdded because his team -  with an average offense - would be expected to win 90% of the time anyway.
