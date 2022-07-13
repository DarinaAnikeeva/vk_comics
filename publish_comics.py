import requests
import os
import random

from dotenv import load_dotenv
from comics_helper import create_url, save_photos


def send_comic_to_server(access_token, group_id, picture):
    payload = {
        'access_token': access_token,
        'group_id': group_id,
        "v": 5.131              # последняя версия API
    }
    response = requests.get(create_url('photos.getWallUploadServer'), params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    with open(picture, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
        response.raise_for_status()
    return response.json()


def save_comic_to_album(access_token, group_id, picture):
    picture_params = send_comic_to_server(access_token, group_id, picture)
    album_picture_payload = {
        "server": picture_params['server'],
        'photo': picture_params['photo'],
        'hash': picture_params['hash'],
        'group_id': group_id,
        'access_token': access_token,
        "v": 5.131,
    }
    album_picture_response = requests.post(create_url('photos.saveWallPhoto'), params=album_picture_payload)
    album_picture_response.raise_for_status()
    picture_id = album_picture_response.json()['response'][0]['id']
    picture_owner_id = album_picture_response.json()['response'][0]['owner_id']
    return picture_id, picture_owner_id


def send_comic_to_wall(access_token, group_id, message, picture):
    picture_media_id, picture_owner_id = save_comic_to_album(access_token, group_id, picture)
    url = create_url('wall.post')
    wall_picture_payload = {
        'from_group': 1,                                                  # 1 - сообщение от имени группы, 0 - от имени пользователя
        'attachments': f"photo{picture_owner_id}_{picture_media_id}",     #для поиска нужной картинки
        'owner_id': f"-{group_id}",
        'message': message,                                               #текст, который будет в записи
        'access_token': access_token,
        'v': 5.131                                                        #последняя версия API
    }
    wall_picture_response = requests.post(url, params=wall_picture_payload)
    wall_picture_response.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.environ['VK_ACCOUNT_TOKEN']
    group_id = os.environ["VK_GROUP_ID"]

    xkcd_url = f'https://xkcd.com/{random.randint(0, 2644)}/info.0.json'
    xkcd_response = requests.get(xkcd_url)
    xkcd_response.raise_for_status()

    comics_page = xkcd_response.json()
    save_photos(comics_page['img'], 'comic')

    send_comic_to_wall(vk_token, group_id, comics_page['alt'], picture='comic.jpg')

    os.remove('comic.jpg')
