#!/usr/bin/python3

# predictive power
# 0 = always wrong
# 100 = complete random (33% correct)
# 105 = 34.42% correct
# 110 = 35.48% correct
# 200 = 50% correct
# 400 = 66.6% correct
DOWN_POWER = 101
STAY_POWER = 101
UP_POWER = 102

# lower target massively helps reduce bad runs, but profit is capped at target
TARGET = 125

# bailing out at a higher level puts a cap on loss, but also increases bad runs
BAIL = 50

# fiddling with the payout value doesn't do much, higher factor, and lower limit value are more risk averse
PAYOUT_LIMIT = 101
PAYOUT_FACTOR = 0.8

# simulation parameters
STEPS = 300
RUNS = 500

try: # python >= 3.6
    from random import choices
except ImportError: # python <= 3.5
    from random import choice, random as rnd
    def choices(lst, weights):
        """
        my own shitty implementation of something that exists in python >= 3.6
        """
        assert len(lst) == len(weights)
        tot = sum(weights)
        chk = rnd() * tot
        idx = 0
        for crt in weights:
            if chk < crt:
                return lst[idx]
            chk -= crt
            idx += 1
        return seq[-1]

class Crypto:
    def __init__(self, symbol):
        self.symbol = symbol
        self.price = 1

    def change(self, down_stay_up = [1,1,1]):
        changes = [0.95, 1, 1.05]
        self.price *= choices(changes, weights=down_stay_up)

class Exchange:
    def __init__(self):
        self._cryptos = dict()

    def price(self, crypto):
        return self._cryptos[crypto].price

    def cryptos(self):
        return self._cryptos.keys()

    def add_crypto(self, symbol):
        self._cryptos[symbol] = Crypto(symbol)

    def change_price(self, symbol, down_stay_up):
        weights = {
            'down': [DOWN_POWER, 100, 100],
            'stay': [100, STAY_POWER, 100],
            'up': [100, 100, UP_POWER]
        }
        self._cryptos[symbol].change(weights[down_stay_up])

    def __str__(self):
        ret = ""
        for crypto in self._cryptos:
            ret += "{} has price of {}\n".format(crypto, self._cryptos[crypto].price)
        return ret

class Predictor:
    def __init__(self):
        self.predictions = dict()

    def predict(self, exchange):
        for crypto in exchange.cryptos():
            prediction = choice(['up', 'down', 'stay'])
            self.predictions[crypto] = prediction

    def apply(self, exchange):
        for crypto in self.predictions:
            exchange.change_price(crypto, self.predictions[crypto])

class Manager:
    def __init__(self, pr, xc, funds=100):
        self._step_counter = 0
        self.funds = funds
        self.pr = pr
        self.xc = xc
        self.payout = 0
        self.portfolio = dict()
        self.done = False

    def check_payout(self):
        if self.funds >= PAYOUT_LIMIT:
            pay = (self.funds - PAYOUT_LIMIT) * PAYOUT_FACTOR
            self.payout += pay
            self.funds -= pay

    def buy(self, crypto):
        if self.funds < 1:
            return
        invest = self.funds * 0.50
        self.funds -= invest
        buying = invest/self.xc.price(crypto)
        if crypto not in self.portfolio:
            self.portfolio[crypto] = buying
        else:
            self.portfolio[crypto] += buying

    def sell(self, crypto):
        if crypto not in self.portfolio:
            return
        price = self.xc.price(crypto)
        self.funds += self.portfolio[crypto] * price
        self.portfolio[crypto] = 0

    def step(self):
        self._step_counter += 1
        total = self.total_value()
        if self.done or total > TARGET or total < BAIL:
            self.done = True
            return
        for c in self.xc.cryptos():
            if self.pr.predictions.get(c) == 'stay':
                continue
            elif self.pr.predictions.get(c) == 'up':
                self.buy(c)
            elif self.pr.predictions.get(c) == 'down':
                self.sell(c)
        self.check_payout()

    def total_value(self):
        value = self.funds + self.payout
        for crypto in self.portfolio:
            value += self.portfolio[crypto] * self.xc.price(crypto)
        return value

    def __str__(self):
        ret = ""
        ret += "Funds: {}\n".format(self.funds)
        ret += "Payout: {}\n".format(self.payout)
        ret += "Total Val: {}\n".format(self.total_value())
        return ret

def run(steps=STEPS):
    xc = Exchange()
    xc.add_crypto('btc')
    xc.add_crypto('eth')
    xc.add_crypto('lat')

    pr = Predictor()

    mn = Manager(pr, xc)

    for i in range(0,steps):
        pr.predict(xc)
        mn.step()
        if mn.done:
            return mn.total_value()
        pr.apply(xc)
    
    return mn.total_value()

def runSteps(_=None):
    return run()

runs = RUNS
from multiprocessing import Pool
with Pool(16) as p:
    results = p.map(runSteps, range(0, runs))
    #results = [run() for i in range(0,runs)]

good = sum([r>100 for r in results])
good_p = round(good/runs * 100, 1)
bad = sum([r<100 for r in results])
bad_p = round(bad/runs * 100, 1)

print("Did {} runs with {} steps each".format(len(results), STEPS))
print("Best:", max(results))
print("Worst:", min(results))
print("Average:", sum(results)/runs)
print("Good runs: {}%".format(good_p))
print("Bad runs: {}%".format(bad_p))

