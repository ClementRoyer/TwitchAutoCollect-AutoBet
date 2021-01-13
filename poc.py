from config_loader import load
from selenium import webdriver
from datetime import datetime
from utils import *
from decision import betStrategy
from gql_request import getStreamCoins
import os
import time
import signal
import sys

# TODO : Move to subfolder and user folder.file to import

DEBUG       = True
STREAM      = ''
TOKEN       = ''

TIMEOUT     = 10 # sec; query timeout
REFRESH     = 10 # sec; check for bet and chest
TWITCH_URL  = 'https://www.twitch.tv/'
USER_AGENT  = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

cookiePolicyQuery               = 'button[data-a-target="consent-banner-accept"]'
matureContentQuery              = 'button[data-a-target="player-overlay-mature-accept"]'
sidebarQuery                    = '*[data-test-selector="user-menu__toggle"]'
userStatusQuery                 = 'span[data-a-target="presence-text"]'
streamPauseQuery                = 'button[data-a-target="player-play-pause-button"]'
streamSettingsQuery             = '[data-a-target="player-settings-button"]'
streamQualitySettingQuery       = '[data-a-target="player-settings-menu-item-quality"]'
streamQualityQuery              = "//div[@data-a-target='player-settings-submenu-quality-option']//div[contains(text(), '160p')]"

streamCoins                     = '[data-test-selector="balance-string"]'
streamCoinsChestQuery           = 'button[class="tw-button tw-button--success tw-interactive"]'
streamCoinsMenuXP               = '//div[@data-test-selector="community-points-summary"]//button'
streamCoinsAcceptFirstUsageXP   = "//*[@id='channel-points-reward-center-body']/div[1]/div[1]/div[2]//button/div"
streamBetSubTitle               = '[data-test-selector="predictions-list-item__subtitle"]'
streamBetTitle                  = '[data-test-selector="community-prediction-highlight-header-title"]'
streamBetTitleInBet             = '[data-test-selector="predictions-list-item__title"]'
streamBetRemainingTime          = "div#channel-points-reward-center-body>div>div>div>div>div>div>div>p:nth-of-type(2)"
streamBetTitleNoXP              = "//div[@id='channel-points-reward-center-body']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]"
streamBetTitleYesXP             = "//div[@id='channel-points-reward-center-body']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]"
streamBetButtonNoXP             = "//div[@id='channel-points-reward-center-body']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/button[1]"
streamBetButtonYesXP            = "//div[@id='channel-points-reward-center-body']/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/button[1]"# ok
streamStatsViewers              = "[data-a-target='animated-channel-viewers-count']"
streamBetStatsCoteYesXP         = "(//div[@class='prediction-summary-stat__value tw-inline-flex']//p)[2]"
streamBetStatsCoteNoXP          = "(//div[@class='prediction-summary-stat__value tw-inline-flex']//p)[6]"
streamBetCustomVote             = '[data-test-selector="prediction-checkout-active-footer__input-type-toggle"]'
streamBetVoteXP                 = "(//input[contains(@class,'tw-block tw-border-bottom-left-radius-medium')])" # [2] =yes, [3] = no
streamBetWinInMenu              = '[data-test-selector="prediction-checkout-completion-step__winnings-string"]'


class Bet:
    '''Bet class'''
    active = False
    endTime = datetime.now()
    title = ""
    predictionA = ""
    predictionB = ""
    coteA = ""
    coteB = ""
    prediction = ""
    amount = 0


def signal_handler(sig, frame):
    exit()


def exit():
    chrome.close()
    os.remove("debug.log")
    sys.exit(0)


def print_bet_stats(bet):
    print("\n💸 Bet info")
    print("📌 Title         : '" + bet.title + "'")
    print("📌 Prediction A  : '" + bet.predictionA + "' | Cote : " + bet.coteA + ".")
    print("📌 Prediction B  : '" + bet.predictionB + "' | Cote : " + bet.coteB + ".")
    print("📌 My prediction : " + bet.prediction)
    print("💰 Bet placed    :", bet.amount)


def print_stats(chrome):
    clickWhenExist(chrome, sidebarQuery)                                # - open side bar
    status = getWhenExist(chrome, userStatusQuery)                      # - get current user status
    clickWhenExist(chrome, sidebarQuery)                                # - close side bar
    coins = getWhenExist(chrome, streamCoins)                           # get current user status
    viewers = getWhenExist(chrome, streamStatsViewers)
    
    print('\n⏳ Time: ' + datetime.now().strftime('%H:%M:%S'))
    print('📽️ ' + STREAM.capitalize() + ' | 👽 ' + str(viewers) + ' viewers.')
    # print('📌 Current status: ' + status + '.')                      # TODO : Bug
    print('💰 Coins: ' + coins + '.')


def init_watching(chrome):
    print('🍪   Cookies: ', end='')
    clickWhenExist(chrome, cookiePolicyQuery)                               # Accept cookies
    print('✔️\n🔞   Mature content: ', end='')
    clickIfExist(chrome, matureContentQuery)                                # Accept mature content
    print('✔️\n⚙️   Setting lowest possible resolution: ', end='')
    clickWhenExist(chrome, streamPauseQuery)                                # - Pause
    clickWhenExist(chrome, streamSettingsQuery)                             # Open setting menu
    clickWhenExist(chrome, streamQualitySettingQuery)                       # Open quality setting
    clickIfExistXP(chrome, streamQualityQuery)                              # Click on 160p
    clickWhenExist(chrome, streamPauseQuery)                                # - Play
    print('✔️\n🔓   Accepting coins policy: ', end='')
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Open coins menu
    clickIfExistXP(chrome, streamCoinsAcceptFirstUsageXP)                   # Accept coins policy
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Close coins menu
    print('✔️')


def fillBet(chrome, bet):
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Open coins menu
    bet.title = getWhenExist(chrome, streamBetTitleInBet)                   # Get bet title
    clickWhenExist(chrome, streamBetTitleInBet)                             # Click on the bet
    bet.predictionA = getWhenExistXP(chrome, streamBetTitleYesXP)           # Title A
    bet.predictionB = getWhenExistXP(chrome, streamBetTitleNoXP)            # Title B
    bet.coteA = getWhenExistXP(chrome, streamBetStatsCoteYesXP)[2:]         # Get cote A
    bet.coteB = getWhenExistXP(chrome, streamBetStatsCoteNoXP)[2:]          # Get cote B
    remaining_time = getWhenExist(chrome, streamBetRemainingTime)           # Get time to bet
    remaining_time = remaining_time[remaining_time.find(':')-2:remaining_time.find(':')+3].replace(" ", "")
    bet.endTime = time.strptime(remaining_time.replace(" ", ""), "%M:%S")   # Set end time
    bet.amount = getStreamCoins(TOKEN, STREAM)                              # Set amount to all points
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Close coins menu


def handleBetInProgress(chrome, bet):
    if not doesExist(chrome, streamBetTitle):                               # If title in chat, then bet is over
        return
    
    title = getWhenExist(chrome, streamBetTitle)
    if (bet.title + ' ' + bet.prediction == title):
        bet.active = False
        print("🏆 Bet won !")
    elif bet.title + ' ' + bet.prediction == title:
        bet.active = False
        print("😅 Bet Lose !")


def placeBet(chrome, bet):
    # bet.active = True
    # second = max((bet.endTime.tm_sec + bet.endTime.tm_min * 60) - 30, 0)    # -20 to still have 20 sec to bet, may reduce this number later
    # print("sleeping", second)
    # time.sleep(second)                                                      # Wait until last moment to place the bet
    fillBet(chrome, bet)                                                    # Get lastest data
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Open coins menu
    clickWhenExist(chrome, streamBetTitleInBet)                             # Click on the bet
    clickWhenExist(chrome, streamBetCustomVote)                             # Enable input of custom value


    decision = betStrategy(chrome, bet)                                     # Take your strategy

    if decision['choice'] == 'A':                                           # Vote on A
        bet.prediction = bet.predictionA
        selector = streamBetVoteXP + "[2]"
        sendText(chrome, selector, decision['amount'])
        clickWhenExistXP(chrome, streamBetButtonYesXP)
    else:                                                                   # Vote on B
        bet.prediction = bet.predictionB
        selector = streamBetVoteXP + "[3]"
        sendText(chrome, selector, decision['amount'])
        clickWhenExistXP(chrome, streamBetButtonNoXP)

    bet.amount = decision['amount']
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Close coins menu


def checkAndPlaceBet(chrome, bet):
    if not doesExist(chrome, streamBetTitle):
        return

    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Open coins menu
    subtitle = getWhenExist(chrome, streamBetSubTitle)                      # Get bet subtitle
    clickIfExistXP(chrome, streamCoinsMenuXP)                               # Close coins menu
    
    if subtitle is None or subtitle.find(':') == -1:
        return

    print('\n\n🔔 Bet found ! 🔔')
    fillBet(chrome, bet)
    placeBet(chrome, bet)
    print_bet_stats(bet)
    time.sleep(120)


def handleBet(chrome, bet):
    
    if not bet.active:
        checkAndPlaceBet(chrome, bet)
    else:
        handleBetInProgress(chrome, bet)


def collectAndBet(chrome, stream_url):
    chrome.get(stream_url)
    init_watching(chrome)
    bet = Bet()

    print("\n\n🔔 Starting to collect & bet 🔔\n")
    end = False
    balance = 0
    while not end:
        clickIfExist(chrome, streamCoinsChestQuery)                                         # Collect chest

        newBalance = getStreamCoins(STREAM, TOKEN)                                          # To not spam the output
        if balance != newBalance:
            print_stats(chrome)
            balance = newBalance

        handleBet(chrome, bet)

        time.sleep(REFRESH)

 
def loadTwitch(chrome):
    cookie = {
        "domain": ".twitch.tv",
        "hostOnly": False,
        "httpOnly": False,
        "name": "auth-token",
        "path": "/",
        "SameSite": "no_restriction",
        "secure": True,
        "session": False,
        "storeId": "0",
        "id": 1,
        "value": TOKEN }
    chrome.get(TWITCH_URL)
    chrome.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": USER_AGENT})
    chrome.add_cookie(cookie)


def __init(settings):
    print('🛠️   Initialization')
    global STREAM, DEBUG, TOKEN
    TOKEN = settings['token']
    STREAM = settings['stream']
    DEBUG = settings['debug']
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--mute-audio')
    if not DEBUG:
        chrome_options.add_argument('headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-accelerated-2d-canvas')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-zygote')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(settings['chrome_path'], options=chrome_options)
    driver.set_window_size(1366, 768)
    driver.implicitly_wait(2)
    return driver


if __name__ == "__main__":
    chrome = __init(load(os.path.abspath(os.getcwd()) + '\\config.txt'))
    loadTwitch(chrome)
    collectAndBet(chrome, TWITCH_URL + STREAM)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGSEGV, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
