from flask import Flask, make_response, request, redirect
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz, process
import re
import requests
import sys

app = Flask(__name__)

@app.route("/")
def download_anime():
    try:
        anime_name_input = request.args.get('anime', '')
        episode = request.args.get('episode', '')

        if anime_name_input == '':
            raise Exception('Include an anime name!' + '<br />' + 'Usage: ' + request.url + '?anime=[ANIME NAME]&episode=[EPISODE NUMBER]')
        if episode == '':
            raise Exception('Include an episode!' + '<br />' + 'Usage: ' + request.url + '?anime=[ANIME NAME]&episode=[EPISODE NUMBER]')

        soup = BeautifulSoup(requests.get('http://www.chia-anime.com/index').content)

        animes = []

        # Get anime pages from index page
        for link in soup.find_all(href=re.compile(re.escape('http://www.chia-anime.com/category/'))):
            anime_name = link.get('href')[35:]
            animes.append(anime_name)

        # Get the best matching anime from the list compared to the user supplied name
        anime_name, anime_score = process.extractOne(anime_name_input, animes)

        if anime_score >= 75:
            print 'Found ' + anime_name + '! (Score: ' + str(anime_score) + ').'
        else:
            raise Exception('Anime not found: ' + anime_name_input + '.' + '<br />' + 'Best match: ' + anime_name + ' (' + str(anime_score) + ').')

        # Get the anime page
        soup = BeautifulSoup(requests.get('http://www.chia-anime.com/category/' + anime_name).content)

        # Deal with some weird naming stuff
        anime_url = anime_name
        if anime_name[-5:] == 'anime':
            anime_url = anime_name[:-6]

        urlHasEpisode = True

        # Get the anime episode download link
        for link in soup.find_all(href=re.compile(re.escape('http://www.chia-anime.com/' + anime_name + '/' + anime_url))):
            href = link.get('href')
            startIndex = href.find(anime_name) + len(anime_name) + len(anime_url) + 10
            endIndex = href.find('-', startIndex)
            if endIndex == -1:
                endIndex = len(href)
            if link.get('href')[startIndex:endIndex] == episode:
                print 'Found episode ' + episode + '!'
                break;
            else:
                startIndex -= 8 # No 'episode' in download URL
                if (link.get('href')[startIndex:endIndex] == episode):
                    print 'Found episode ' + episode + '!'
                    urlHasEpisode = False
                    break;
        else:
            print 'Episode not found: ' + episode + '.'
            quit()

        # Get the episode page
        if urlHasEpisode:
            soup = BeautifulSoup(requests.get('http://www.chia-anime.com/' + anime_name + '/' + anime_url + '-episode-' + episode).content)
        else:
            soup = BeautifulSoup(requests.get('http://www.chia-anime.com/' + anime_name + '/' + anime_url + '-' + episode).content)

        # Find the download page link
        downloadPage = soup.find_all(href=re.compile(re.escape('http://download.animepremium.tv/video')))[0].get('href')

        finalUrl = "/"

        # Get the direct link to the file, either in the form 'animepremium.tv:8880/download' or '.mp4'.
        soup = BeautifulSoup(requests.get(downloadPage).content)
        for link in soup.find_all(href=re.compile(re.escape('animepremium.tv:8880/download'))):
            finalUrl = link.get('href')
            break;
        else:
            for link in soup.find_all(href=re.compile(re.escape('.mp4/'))):
                finalUrl = 'http://download.animepremium.tv/get/' + link.get('href')
                break;
            else:
                print 'Error.'

        return redirect(finalUrl, code=302)
    except Exception, e:
        return str(e)

if __name__ == "__main__":
    app.run()