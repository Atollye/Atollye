import allure
import pytest

from shared_modules.helpers import is_date_valid, assert_response_code
from shared_modules.ffsec_client.helpers import generate_events, get_job_id
from shared_modules.helpers_api import HelpersApi as help
from shared_modules.vw_detects import rnd_face, rnd_face_2, face_beard_eye
from shared_modules.vw_detects import body_red_bottom_blue_top, car_daewoo_1


create_props = {
    "name": "Test watchlist",
    "comment": "asdfasdf testtest testttesetsdfzxcv vzxcvzsder",
    "color": "C70606",
    "camera_groups": [],
    "active": True
}

WATCH_LIST_ID = 2
DEFAULT_COUNT_WATCH_LISTS = 2


@allure.feature('Watch-lists')
@pytest.mark.usefixtures('restore_base_state', 'enable_body', 'enable_car')
class TestWatchLists:

    @allure.title('Проверка наличия дефолтного watch-list и unmatched')
    def test_default_watch_list(self, api_client):
        resp = api_client.watch_lists.GET()
        assert_response_code(resp.status_code, 200, resp.text)
        watch_list = resp.json().get('results')
        assert len(watch_list) == DEFAULT_COUNT_WATCH_LISTS
        sorted_watch_list = sorted(watch_list, key=lambda k: k['id'])
        assert sorted_watch_list[0].get('id') == -1 and\
               sorted_watch_list[0].get('name') == "Unmatched"
        assert sorted_watch_list[1].get('id') == 1 and\
               sorted_watch_list[1].get('name') == "Default Watch List"

    @allure.title('Добавление нового watch-list')
    def test_add_new_watch_list(self, api_client):
        api_client.data = create_props
        resp = api_client.watch_lists.POST()
        assert resp.status_code == 201,\
            "Неправильный код ответа на запрос добавления watch-list."

    @allure.title('Получение списка watch-lists')
    def test_get_watch_lists(self, api_client):
        resp = api_client.watch_lists.GET()

        assert resp.status_code == 200, "Неправильный код ответа на запрос получения watch-lists"
        assert len(resp.json().get('results')) == DEFAULT_COUNT_WATCH_LISTS+1,\
            "Неправильное количество watch-lists"
        for res in resp.json().get('results'):
            assert (is_date_valid(res.get('created_date')) and
                    is_date_valid(res.get('modified_date')) and
                    res.get('active')), "Некорректные свойства для watch-lists"

    @allure.title('Получение watch-list по id')
    def test_get_watch_list_by_id(self, api_client):
        resp = api_client.watch_lists.id(WATCH_LIST_ID).GET()

        assert resp.status_code == 200,\
            f"Неправильный код ответа на запрос получения watch-list c id-{WATCH_LIST_ID}"
        assert (is_date_valid(resp.json().get('created_date')) and
                is_date_valid(resp.json().get('modified_date')) and
                resp.json().get('active')), "Некорректные свойства для watch-list"

    @pytest.mark.parametrize('invalid_id', [55, 'qwer', '!?@'])
    @allure.title('Получение watch-list с невалидным id')
    def test_get_watch_list_by_invalid_id(self, api_client, invalid_id):
        resp = api_client.watch_lists.id(5).GET()

        assert resp.status_code == 404,\
            f"Неправильный код ответа на запрос получения watch-list c id-{WATCH_LIST_ID}"

    @allure.title('Обновление свойств watch-list')
    def test_update_watch_list_props(self, api_client):
        create_props['name'] = 'New name watchlist'
        api_client.data = create_props
        resp = api_client.watch_lists.id(WATCH_LIST_ID).PATCH()

        assert resp.status_code == 200, "Неправильный код ответа на запрос обновления свойств watch-list"
        assert resp.json().get('name') == create_props['name'], \
            "Не удалось поменять имя для watch-list с id-{}".format(WATCH_LIST_ID)

    @pytest.mark.parametrize('prop, invalid_val', [
        ("active", "xxxx"),
        ("name", ""),
        ("color", "ffccffxx")
    ])
    @allure.title('Обновление watch-list с невалидными свойствами')
    def test_update_watch_list_invalid_props(self, api_client, prop, invalid_val):
        create_props[prop] = invalid_val
        api_client.data = create_props
        resp = api_client.watch_lists.id(WATCH_LIST_ID).PATCH()

        assert resp.status_code == 400,\
            "Неправильный код ответа на запрос с невалидными свойствами для watch-list"

    @allure.title('Обновление watch-list с невалидными json')
    def test_update_watch_list_invalid_json(self, api_client):
        api_client.data = "xxxx"
        resp = api_client.watch_lists.id(WATCH_LIST_ID).PATCH()

        assert resp.status_code in (400, 415),\
            "Неправильный код ответа на запрос с невалидным json для watch-list"

    @allure.title('Удаление всех карт из watch-list')
    def test_purge_watch_list(self, api_client):
        resp = api_client.watch_lists.id(WATCH_LIST_ID).purge.POST()

        assert resp.status_code == 204,\
            "Неправильный код ответа на запрос удаления всех карт из watch-list"

    @allure.title('Удаление созданного watch-list')
    def test_delete_watch_list(self, api_client):
        resp = api_client.watch_lists.id(WATCH_LIST_ID).DELETE()

        assert resp.status_code == 204, "Неправильный код ответа на запрос удаления watch-list"
        assert len(api_client.watch_lists.GET().json().get('results')) == 2, \
            "Неудалось удалить watch-list с id-{}".format(WATCH_LIST_ID)

    @allure.title('Дефолтный watch-list не должен удаляться')
    def test_delete_default_watch_list(self, api_client):
        resp = api_client.watch_lists.id(1).DELETE()
        assert_response_code(resp.status_code, 400, resp.text)

    @allure.title('Удаление всех карт из всех watch-lists')
    def test_purge_all_watch_lists(self, api_client):
        with allure.step('Создаем карточку человека c несколькими лицами и телом'):
            custom_wl = help.add_watch_list(api_client)['id']
            card_1 = help.add_card(
                api_client, name='Gal Gadot', watch_lists = [custom_wl],
                photo_path=rnd_face.photo_path
            )['id']
            help.add_object_face(
                api_client, card_id=card_1, photo_path=rnd_face_2.photo_path
            )
            help.add_object_body(
                api_client, card_id=card_1, 
                photo_path=body_red_bottom_blue_top.photo_path
            )

        with allure.step('Создаем карточку, привязанную к двум WL'):            
            card_2 = help.add_card(
                api_client, name='Man with beard',
                watch_lists = [1, custom_wl],
                photo_path=face_beard_eye.photo_path
            )['id']

        with allure.step('Создаем карточку машины'):
            card_3 = help.add_card(
                api_client, name="Gal Gadot's car", 
                card_type='car', watch_lists=[1],
                photo_path=car_daewoo_1.photo_path
            )['id']

        with allure.step('Создаем сматченное событие'):                         
            job_id = get_job_id(help.add_camera(api_client)['id'])
            for detect in rnd_face_2,  car_daewoo_1:
                generate_events(api_client, job_id, detect)

        with allure.step('Создаем связь между карточками'): 
            relation_1 = help.add_relation(api_client)['id']
            for card, card_type in [(card_1, 'human'), (card_3, 'car')]:
                help.add_relation_link(
                    api_client, relation=relation_1, 
                    card=card, card_type=card_type
                )

        with allure.step('Чистим все WL и проверяем, что очистка сработала:'):
            resp = api_client.watch_lists.purge_all.POST()
            assert_response_code(
                resp.status_code, 200, 
                'Неправильный код ответа на запрос watch-lists/purge_all/'
            )
            for method in ('cards_humans', 'cards_cars'):
                resp = getattr(api_client, method).GET()
                assert_response_code(resp.status_code, 200, resp.text)
                cards = resp.json().get('results')
                assert not len(cards), 'Запрос watch-lists/purge_all удалил не все карточки'

