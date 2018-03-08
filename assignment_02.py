import csv, time, random
from bs4 import BeautifulSoup
from selenium import webdriver


X_PATHS = [
           ['//*[@id="sp_hitting-0"]/fieldset[1]', '//*[@id="sp_hitting_season"]/option[4]',
            '//*[@id="top_nav"]/div/ul/li[5]', '//*[@id="st_hitting_game_type"]',
            '//*[@id="st_hitting_game_type"]/option[1]'],
           ['//*[@id="sp_parent"]', '//*[@id="sp_hitting_season"]', '//*[@id="sp_hitting_season"]/option[2]',
            '//*[@id="sp_hitting_team_id"]', '//*[@id="sp_hitting_team_id"]/option[20]',
            '//*[@id="sp_hitting_hitting_splits"]', '//*[@id="sp_hitting_hitting_splits"]/option'],
           ['// *[ @ id = "sp_hitting_season"]', '//*[@id="sp_hitting_season"]/option[4]',
            '//*[@id="sp_hitting-1"]/fieldset[1]/label[2]/span', '//*[@id="sp_hitting_team_id"]',
            '//*[@id="sp_hitting_team_id"]/option[1]']
        ]


BASE_URL = "http://mlb.mlb.com/stats/sortable.jsp#elem=%5Bobject+Object%5D&tab_level=child&click_text=Sortable+Player+hitting&game_type='S'&season=2018&season_type=ANY&league_code='MLB'&sectionType=sp&statType=hitting&page=1&ts=1520478568794"


def __csv_writer(q_num, column_names, ltd):
    with open('Question_question%s.csv' % q_num, 'w') as f:
        csv_obj = csv.DictWriter(f, column_names)
        csv_obj.writerows(ltd)


def __get_ans(soup_val, params):
    ret_val = []

    for tr in soup_val.find_all('table')[0].find('tbody'):
        ret_val.append({param[0]: tr.find('td', {'index': param[1]}).get_text() for param in params})

    return ret_val


def run():
    driver = webdriver.Chrome('C:\\Users\\soura\\Desktop\\chromedriver')

    driver.get(BASE_URL)

    time.sleep(5)

    q1_xpaths = X_PATHS[0]

    for xq1 in q1_xpaths:
        driver.find_element_by_xpath(xq1).click()
        time.sleep(random.randint(1, 5))

    soup_q1 = BeautifulSoup(driver.page_source, 'html.parser')

    q1 = __get_ans(soup_q1, [('team', 1), ('league', 3), ('HR', 10)])

    __csv_writer('1', ['team', 'league', 'HR'], q1)

    print(sorted(q1, key=lambda x: x['HR'])[-1]['team'])

    al = [int(i['HR']) for i in filter(lambda x: x['league'] == 'AL', q1)]
    nl = [int(i['HR']) for i in filter(lambda x: x['league'] == 'NL', q1)]

    if sum(al) / len(al) > sum(nl) / len(nl):
        print('AL ' + str(sum(al) / len(al)))
    else:
        print('NL ' + str(sum(nl) / len(nl)))

    __csv_writer('2a', ['team', 'league', 'HR'], q1)

    select_element = driver.find_element_by_xpath('//*[@id="st_hitting_hitting_splits"]')
    select_element.click()

    time.sleep(random.randint(1, 5))

    select_element.find_element_by_xpath('//*[@id="st_hitting_hitting_splits"]/optgroup[12]/option[1]').click()

    time.sleep(random.randint(1, 5))

    soup_q2 = BeautifulSoup(driver.page_source, 'html.parser')

    q2 = __get_ans(soup_q2, [('team', 1), ('league', 3), ('HR', 10)])

    __csv_writer('2b', ['team', 'league', 'HR'], q2)

    fal = [int(i['HR']) for i in filter(lambda x: x['league'] == 'AL', q2)]
    fnl = [int(i['HR']) for i in filter(lambda x: x['league'] == 'NL', q2)]

    if sum(fal) / len(fal) > sum(fnl) / len(fnl):
        print('AL ' + str(sum(fal) / len(fal)))
    else:
        print('NL ' + str(sum(fnl) / len(fnl)))

    time.sleep(random.randint(1, 5))

    se_player = driver.find_element_by_xpath('//*[@id="top_nav"]')
    p2_xpaths = X_PATHS[1]

    for xp2 in p2_xpaths:
        se_player.find_element_by_xpath(xp2).click()
        time.sleep(random.randint(1, 5))

    soup_q3 = BeautifulSoup(driver.page_source, 'html.parser')

    q3 = []
    for tr in soup_q3.find_all('table')[0].find('tbody'):
        q3.append({'player': tr.find('a').get_text(),
                   'position': tr.find('td', {'index': 5}).get_text(),
                   'ab': tr.find('td', {'index': 7}).get_text(),
                   'avg': tr.find('td', {'index': 18}).get_text()})

    __csv_writer('3a', ['player', 'position', 'ab', 'avg'], q3)

    val = sorted(q3, key=lambda x: int(x['ab']) > 30)[0]
    print(val['player'] + ' ' + val['position'])

    __csv_writer('3b', ['player', 'position', 'ab', 'avg'], q3)

    val_b = sorted([s for s in q3 if s['position'] in ['RF', 'CF', 'LF'] and s['avg'] != '.---'], key=lambda x: x['avg'])[-1]
    print(val_b['player'] + ' ' + val_b['position'])

    p3_xpaths = X_PATHS[2]

    for xp3 in p3_xpaths:
        driver.find_element_by_xpath(xp3).click()
        time.sleep(random.randint(1, 5))

    soup_top_al = BeautifulSoup(driver.page_source, 'html.parser')

    t_al = []
    for tr in soup_top_al.find_all('table')[0].find('tbody'):
        t_al.append({'player': tr.find('a').get_text(),
                     'position': tr.find('td', {'index': 5}).get_text(),
                     'ab': tr.find('td', {'index': 7}).get_text()})

    __csv_writer('4', ['player', 'position', 'ab'], t_al)

    ans_4 = sorted(t_al, key=lambda x: int(x['ab']))[-1]

    print(ans_4['player'] + ' ' + ans_4['ab'] + ' ' + ans_4['position'])

    driver.quit()


run()

