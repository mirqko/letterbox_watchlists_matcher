# Python built-in modules
from pprint import pprint

# Python external modules
import bs4
import requests

LETTERBOX_BASELINK = 'https://letterboxd.com/{user}/watchlist/page/{page_num}'


class LetterboxMatcher:
    def __init__(self, debug=True):
        self.users = []
        self.global_watchlist = []
        self.debug = debug

    def check_user_pages(self, user):
        """check how many watchlist pages a user has
        :param user: letterbox username(str)
        """
        user_home = LETTERBOX_BASELINK.format(user=user, page_num='1')
        response = requests.get(user_home)
        response.raise_for_status()
        self.soup = bs4.BeautifulSoup(response.text, 'html.parser')
        page_div = self.soup.find('div', class_='paginate-pages')
        pages = len(page_div.find_all('li'))
        return pages

    def get_user_watchlist(self, user, pages):
        """return a list of films from a given user and number of watchlist pages
        :param user: letterbox username(str)
        :param pages: user's number of watchlist pages(int)
        """
        watchlist = []
        if self.debug:
            print('# --- scraping {} watchlist, found {} pages'.format(user, pages))
        for page_num in range(1, pages + 1):
            if self.debug:
                print('# --- scraping page n {}'.format(page_num))
            page_watchlist = []
            watchlist_page = LETTERBOX_BASELINK.format(user=user, page_num=page_num)
            response = requests.get(watchlist_page)
            response.raise_for_status()
            self.soup = bs4.BeautifulSoup(response.text, 'html.parser')
            ul_films = self.soup.find('ul', class_='poster-list -p125 -grid -scaled128')
            films = ul_films.find_all('img')
            for film in films:
                film = str(film.get('alt'))
                page_watchlist.append(film)
            watchlist += page_watchlist
        return watchlist

    def matching_users_watchlists(self, users_list):
        """scrape the list of n users and return a list of common films inside their watchlists
           :param users_list: list of letterbox usernames(list)
        """
        global_watchlist = []
        first = True
        for user in users_list:
            pages_num = self.check_user_pages(user)
            user_watchlist = self.get_user_watchlist(user, pages_num)
            if first:
                global_watchlist = user_watchlist
                first = False
            else:
                global_watchlist = [film for film in user_watchlist if film in global_watchlist]
        print('# --- found {} common films inside users watchlists'.format(len(global_watchlist)))
        return global_watchlist


if __name__ == '__main__':
    matcher = LetterboxMatcher(debug=True)
    common = matcher.matching_users_watchlists(['xeilean', 'mirqo'])
    pprint(common)