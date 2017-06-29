# AgeCalculatorBot

### Telegram: [@AgeCalculatorBot](https://t.me/AgeCalculatorBot)

#### Know more about your birthday!
#### This Telegram bot calculates interesting data for your birthday.

## Contents
[Functions](#functions)  
[Installation](#installation)  
[Screenshots](#screenshots)  
[License](#license)  

## Functions
* Calculates time since birth and time until next birthday
* Calculates age in years, months, days, hours, minutes and seconds
* Calculates the weekday of your birth and the weekdays for the next ten birthdays
* Calculates special events e.g. the date when you get 1,000,000 hours old
* Simple interface for inserting date
* All inputs throug inline buttons
* Choose your lanugage (at the moment english and german available)

## Installation

#### Clone Repository:
```
git clone https://github.com/Andre0512/AgeCalculatorBot.git
cd AgeCalculatorBot/
```

#### Install Telegram framework and yaml support:
```
pip3 install python-telegram-bot pyyaml
```
#### Enter required data into `config.yml`
```
cp config.yml.default config.yml
nano config.yml
```
For this step, you have to register a Telegram bot by the Telegram [@BotFahter](https://t.me/botfather).

You can see your Telegram ID by using the [@userinfobot](https://telegram.me/userinfobot).

#### Start the bot
```
python3 AgeCalculatorBot.py &
```

## Screenshots

### Show results
<img src="images/output.png" width="800"/> 

### Input dialogs
<img src="images/insert_data.png" width="800"/>

## License:
This project stands under GNU General Public License.

Contributions to are welcomed. Tell me if you have a good idea for the project or do a pull request.
