# import necessary packages
import scrapy
import re
from datetime import datetime

# define the class that will be used to scrape the data
class SquadSpider(scrapy.Spider):
    name = 'Transfermarkt_Squad'
    # clubs ids in Transfermarkt
    la_liga_clubs = [13, 131, 142, 150, 237, 331, 366, 367, 368, 418, 472, 621, 630, 681, 714, 897, 940, 993,
                    1049, 1050, 1084, 1108, 1244, 1531, 1533, 2448, 2687, 3302, 3368, 3709, 5358, 7971, 12321, 16795]
    # seasons 2010-11 to 2021-22
    seasons = list(range(2010, 2022))
    # pages to scrape
    urls = []
    for i in la_liga_clubs:
        for j in seasons:
            urls.append('https://www.transfermarkt.com/real-madrid/kader/verein/{}/plus/1/galerie/0?saison_id={}'.format(i, j))
    start_urls = urls

    # extract and clean data
    def parse(self, response):
        # club name
        club = response.css('h1::text').extract_first().strip()
        # get the season using the current url, season is the last number in the url
        current_url = response.request.url
        season = re.findall(r'\d+', current_url)[-1]
        # extract player name and remove padding and new line characters
        player_name = response.css('.hauptlink>a::text').extract()
        player_name = list(map(lambda elem: elem.strip(), player_name))
        empty = ''
        while empty in player_name:
            player_name.remove(empty)
        # extract and clean player position
        player_position = response.css('.inline-table tr+ tr td::text').extract()
        player_position = list(map(lambda elem: elem.strip(), player_position))
        # extract player country. For players with double nationalities, extract only the first one (the country the player represents)
        player_country = response.css('img:first-child.flaggenrahmen::attr(title)').extract()
        # remove the first element as it is the league country
        player_country = player_country[1:]
        # extract and clean players' market value
        market_value = response.css('.rechts.hauptlink::text').extract()
        market_value = [x.replace('€', '') for x in market_value]
        market_value = [x.replace('Th.', '000') for x in market_value]
        market_value = [x.replace('k', '000') for x in market_value]
        # for values in millions we add only 4 zeros and remove the decimal point because values are in the format '00.00m'
        market_value = [x.replace('m', '0000') for x in market_value]
        market_value = [x.replace('.', '') for x in market_value]
        market_value = [x.replace('-', '') for x in market_value]
        # extract date of birth
        date_birth_age = response.css('td.posrela+ td::text').extract()
        # extract date_birth without age
        date_birth = [re.sub(r'\(.*\)', '', x) for x in date_birth_age]
        date_birth = [x.strip() for x in date_birth]
        # change date_birth format from 'Feb 5, 1990' to '1990-02-05' using datetime
        date_birth = [datetime.strptime(x, '%b %d, %Y').strftime('%Y-%m-%d') for x in date_birth]
        # extract and clean player height
        height = response.css('td.posrela+ td+ td+ td+ td::text').extract()
        height = [x.replace('m', '') for x in height]
        height = [x.replace(',', '.') for x in height]
        height = [x.replace('-', '') for x in height]
        # yield extracted data
        yield {'club': club,
               'season': season,
               'player_name': player_name,
               'player_position': player_position,
               'date_of_birth': date_birth,
               'player_country': player_country,
               'player_height': height,
               'market_value': market_value
               }
