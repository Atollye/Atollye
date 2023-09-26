import allure
import pytest

from shared_modules.helpers import assert_response_code
from shared_modules.helpers_api import HelpersApi as help


TEST_USER = {
    'name': 'test_user',
    'real_name': 'test_user',
    'active': True,
    'primary_group': 3,
    'password': '123456',
    'confirm_password': '123456',
}

USUAL_ADMIN = 'usual_admin'
PSSWD = '123456'


@pytest.fixture(scope='class')
def create_usual_admin_and_custom_operator(api_client_class):
    # очистка всех пользователей, созданных в предыдущих прогонах
    resp = api_client_class.users.GET()
    for result in resp.json().get('results'):
        user_id = str(result['id'])
        if not user_id == '1':
            resp = api_client_class.users.id(user_id).DELETE()
            assert_response_code(resp.status_code, 204, resp.text)

    resp = help.add_user(api_client_class, name=USUAL_ADMIN, password=PSSWD)
    pytest.usual_admin_and_operator.append(resp['id'])

    # Включаем у роли Operator права add_user и delete_user, которых
    # у нее по дефолту нет
    add_operator_perms = {
        'permissions': [
            'ffsecurity.view_user', 'ffsecurity.add_user',
            'ffsecurity.change_user', 'ffsecurity.delete_user'
        ]
    }
    api_client_class.data = add_operator_perms
    resp = api_client_class.groups.id(2).PATCH()
    assert_response_code(resp.status_code, 200, resp.text)
    perms = resp.json().get('permissions')
    assert (
        'ffsecurity.add_user' in perms and 'ffsecurity.delete_user' in perms), \
            'Не удалось пропатчить права группы Operator'

    resp = help.add_user(
        api_client_class, primary_group=2, name='custom_operator', password=PSSWD
    )
    pytest.usual_admin_and_operator.append(resp['id'])


@pytest.fixture
def delete_all_custom_users(api_client):
    resp = api_client.users.GET()
    for result in resp.json().get('results'):
        user_id = str(result['id'])
        if not (
            user_id == '1' or
            int(user_id) in pytest.usual_admin_and_operator
        ):
            resp = api_client.users.id(user_id).DELETE()
            assert_response_code(resp.status_code, 204, resp.text)


@allure.feature('Permissions')
class TestCreateDeleteUsers:
    '''
    Что проверяем: пользователи не из группы администраторов не могут
    создавать/удалять пользователей, даже если им выдать соответствующие права

    Термины:
    Суперадмин — это неудаляемый пользователь с id =1 из группы администраторов
    Обычный админ — любой другой пользователь из группы администраторов
    '''
    @pytest.mark.tlcode_ff_1528
    def test_usual_admin_can_view_users(self, api_client):
        resp = api_client.users.GET()
        assert_response_code(
            resp.status_code, 200,
            'Обычный админ не может просматривать пользователей'
        )

    @pytest.mark.tlcode_ff_1522
    @allure.title('Обычный админ может создавать и удалять пользователей')
    def test_usual_admin_can_create_delete_users(
        self, api_client, create_usual_admin_and_custom_operator,
        delete_all_custom_users
    ):
        api_client.authorize(username=USUAL_ADMIN, password=PSSWD)
        api_client.data = TEST_USER
        resp = api_client.users.POST()
        assert_response_code(
            resp.status_code, 201, 'Обычный админ не может создавать пользователей'
        )

        test_user_id = resp.json()['id']
        resp = api_client.users.id(test_user_id).DELETE()
        assert_response_code(
            resp.status_code, 204, 'Обычный админ не может удалять пользователей'
        )

    @pytest.mark.tlcode_ff_1529
    def test_operator_can_view_users(self, api_client):
        resp = api_client.users.GET()
        assert_response_code(
            resp.status_code, 200,
            'Оператор не может просматривать пользователей'
        )

    @pytest.mark.tlcode_ff_1523
    @allure.title('Не админ даже с правом add_user не может создать пользователя')
    def test_operator_cannot_create_users(
        self, api_client, create_usual_admin_and_custom_operator,
        delete_all_custom_users
    ):
        api_client.authorize(username='custom_operator', password=PSSWD)
        api_client.data = TEST_USER
        resp = api_client.users.POST()
        assert_response_code(
            resp.status_code, 403, 'Не админ может создавать пользователей'
        )

    @pytest.mark.tlcode_ff_1527
    @allure.title(
        'Не админ даже с правом delete_user не может удалить пользователя'
        )
    def test_operator_cannot_delete_users(
        self, api_client, create_usual_admin_and_custom_operator,
        delete_all_custom_users
    ):
        usr = help.add_user(api_client, name='test_user', primary_group=3)
        api_client.authorize(username='custom_operator', password=PSSWD)
        resp = api_client.users.id(usr['id']).DELETE()
        # в ffsec для неадмина by design ответ на запросы по другим пользователям
        # 404 'Запрошенный объект User не существует' а не 403 Permission denied
        err_msg = "Ошибка: не админ может удалить пользователя"
        assert_response_code(resp.status_code, 404, err_msg)
        assert resp.text == \
            '{"code":"NOT_FOUND","desc":"No User matches the given query."}', \
            err_msg

    @pytest.mark.tlcode_ff_1524
    @allure.title('Обычный админ не может удалить себя')
    def test_usual_admin_cannot_delete_himself(
        self, api_client, create_usual_admin_and_custom_operator
    ):
        api_client.authorize(username=USUAL_ADMIN, password=PSSWD)
        usual_admin_id = pytest.usual_admin_and_operator[0]
        resp = api_client.users.id(usual_admin_id).DELETE()
        assert_response_code(
            resp.status_code, 403, 'Обычный админ может удалить сам себя'
        )

    @pytest.mark.tlcode_ff_1525
    @allure.title('Суперадмин не может удалить себя')
    def test_superadmin_cannot_delete_himself(self, api_client):
        resp = api_client.users.id('1').DELETE() 
        assert_response_code(
            resp.status_code, 403, 'Суперадмин может удалить сам себя'
        )
