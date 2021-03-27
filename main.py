import logging
import re
from os.path import exists
from random import choice, randint
from string import ascii_lowercase
from time import sleep

import requests
from lxml import etree

ISEARCH_REGEX = re.compile(r'https://isearch.asu.edu/profile/\d+')
EMAIL_REGEX = re.compile(r'mailto:(.*?@asu\.edu)')
PHONE_REGEX = re.compile(r'tel:(\d+)')
PROF_NAME_XPATH = '/html/body/div[4]/div/section/div[1]/section/div/div[1]/h1/div/text()'

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s %(name)s] %(levelname)s: %(message)s',
    datefmt='%m-%d %H:%M',
)


def main():
    csv_init()
    while True:
        name = input('Please input the instructor name here: ')
        get_instructor_info_init(name)


def spoof_email_gen():
    logging.debug('No email found, generating spoof email')
    domain = '@asu.edu'
    letters = ascii_lowercase

    email = f'{"".join(choice(letters) for _ in range(randint(5, 15)))}{domain}'
    logging.debug(f'Spoof email generated: {email}')
    return email


def spoof_phone_gen():
    logging.debug('No phone found, generating spoof phone:')
    first_part = '(480) '
    second_part = randint(100, 1000)
    sleep(0.2)
    third_part = randint(1000, 10000)

    phone = f'{first_part}{second_part}-{third_part}'
    logging.debug(f'Spoof phone number generated: {phone}')
    return phone


def csv_init():
    if not exists('Instructors.csv'):
        logging.debug("No instructors.csv found in current dir, generating...")
        try:
            with open('Instructors.csv', 'w+') as file:
                file.writelines('Name,Number,Email\n')
        except IOError:
            logging.warning('Program does not have permission to generate csv file, aborted.')
            sleep(5)
            exit(-1)

    logging.debug(
        "CSV file init completed..."
        "\n"
    )


def csv_write(prof_name: str, phone: str, email: str):
    if not exists('Instructors.csv'):
        logging.debug("Wait what? what you did do with my newly generated csv file man!")
        csv_init()

    logging.debug("Writing to file...")
    info_list = [prof_name, phone, email]
    with open('Instructors.csv', 'a') as file:
        file.write(','.join(info_list) + '\n')

    logging.debug("Write to file done...")


def get_instructor_info_init(prof_name: str):
    prof_name = prof_name.replace('"', '')
    url = f'https://gcse.asu.edu/search/google/{prof_name}#gsc.tab=0&gsc.q={prof_name}&gsc.sort='
    page = requests.get(url)
    isearch_url_list = re.findall(ISEARCH_REGEX, page.text)

    if not isearch_url_list:
        logging.debug('No isearch url found. This professor name might be spoofed.')
        logging.debug('Generating spoof email and phone number...')
        csv_write(prof_name, spoof_phone_gen(), spoof_email_gen())

    else:
        logging.debug('ISearch website found, please wait...')
        for element in isearch_url_list:
            if get_instructor_info(element, prof_name):
                break
        else:
            logging.debug('All ISearch result seems to be defunct, generating random info...')
            csv_write(prof_name, spoof_phone_gen(), spoof_email_gen())


def get_instructor_info(url: str, prof_name: str) -> bool:
    page = requests.get(url)

    email = re.findall(EMAIL_REGEX, page.text)
    phone = re.findall(PHONE_REGEX, page.text)

    e = etree.HTML(page.text)
    prof_full_name = e.xpath(PROF_NAME_XPATH)

    if prof_full_name:
        logging.debug(f'Found professor: {prof_full_name[0]}')
    else:
        logging.debug(f'Current url does not seem to be legit...')
        return False

    if email:
        email = email[0]
        logging.debug(f'Email found: {email}')
    else:
        email = spoof_email_gen()

    if phone:
        phone = phone[0]
        phone = f'({phone[0:3]}) {phone[3:6]}-{phone[6:]}'
        logging.debug(f'Phone found: {phone}')
    else:
        phone = spoof_phone_gen()

    csv_write(prof_name, phone, email)
    return True


if __name__ == '__main__':
    main()
