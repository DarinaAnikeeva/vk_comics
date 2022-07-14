import requests
import os
import random

from dotenv import load_dotenv
from comics_helper import save_photos


def send_comic_to_server(access_token, group_id, picture):
    send_to_server_url = "https://api.vk.com/method/photos.getWallUploadServer"
    payload = {
        'access_token': access_token,
        'group_id': group_id,
        "v": LAST_API_VERSION
    }
    response = requests.get(send_to_server_url, params=payload)
    response.raise_for_status()
    upload_url = response.json()['response']['upload_url']
    with open(picture, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(upload_url, files=files)
    response.raise_for_status()
    picture_params = response.json()
    return picture_params['server'], picture_params['photo'], picture_params['hash']


def save_comic_to_album(access_token, group_id, picture):
    server, photo, hash = send_comic_to_server(access_token, group_id, picture)
    save_comic_url = "https://api.vk.com/method/photos.saveWallPhoto"
    album_picture_payload = {
        "server": server,
        'photo': photo,
        'hash': hash,
        'group_id': group_id,
        'access_token': access_token,
        "v": LAST_API_VERSION,
    }
    album_picture_response = requests.post(save_comic_url, params=album_picture_payload)
    album_picture_response.raise_for_status()
    picture_id = album_picture_response.json()['response'][0]['id']
    picture_owner_id = album_picture_response.json()['response'][0]['owner_id']
    return picture_id, picture_owner_id


def send_comic_to_wall(access_token, group_id, message, picture):
    picture_media_id, picture_owner_id = save_comic_to_album(access_token, group_id, picture)
    wall_post_url = "https://api.vk.com/method/wall.post"
    wall_picture_payload = {
        'from_group': 1,                                                  # 1 - сообщение от имени группы, 0 - от имени пользователя
        'attachments': f"photo{picture_owner_id}_{picture_media_id}",     #для поиска нужной картинки
        'owner_id': f"-{group_id}",
        'message': message,                                               #текст, который будет в записи
        'access_token': access_token,
        'v': LAST_API_VERSION
    }
    wall_picture_response = requests.post(wall_post_url, params=wall_picture_payload)
    wall_picture_response.raise_for_status()


if __name__ == "__main__":
    load_dotenv()
    vk_token = os.environ['VK_ACCOUNT_TOKEN']
    group_id = os.environ["VK_GROUP_ID"]
    LAST_API_VERSION = 5.131

    xkcd_url = f'https://xkcd.com/{random.randint(0, 2644)}/info.0.json'
    xkcd_response = requests.get(xkcd_url)
    xkcd_response.raise_for_status()

    comics_page = xkcd_response.json()
    try:
        save_photos(comics_page['img'], 'comic')
        send_comic_to_wall(vk_token, group_id, comics_page['alt'], picture='comic.jpg')
    finally:
        os.remove('comic.jpg')
