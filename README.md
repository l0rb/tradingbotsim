# It's a trading bot/portfolio manager simulator

this consits of 3 main parts:
* a class that models an exchange with a number of assets (eg cryptocoins)
there is much to improved here

* a class that simulatos a predictor
this gives predictions to the manager who makes decisions based on it
after the manager made it's decisions the predictions are used to update the prices in the exchange model. there is an element of randomness in this: the prediction have a set chance of being correct. this way we can simulate/test the impact of predictions with a certain predictive power

* a portfolio manager or trading bot
the main thing that is tested here. this also shows how important it is to have proper portfolio management, as even with pretty good predictive powers we can have wildly different good or bad results depending on the settings of the manager. the main factor here is risk control: more risk can increase potential profit but also increases the chance of having losses and the increases the magnitude of losses

