import time

def betStrategy(driver, bet):
    output = {
        "choice": "",
        "amount": 0
    }

    output['choice'] = "A" if bet.coteA > bet.coteB else "B"                             # Take the most advantageous odds 
    output['amount'] = min(round(bet.amount * 0.05), 250000)       # Caped to 250 000, bet 5% of the balance
    return output