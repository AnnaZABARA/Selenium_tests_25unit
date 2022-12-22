import pytest
import hashlib
import datetime
from selenium import webdriver
from selenium.common import ElementNotInteractableException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
# импортируем необходимые составляющие из библиотек

email = "anna-laluna@mail.ru"
password = "skill12345"
#вводим переменные с логином и паролем

def wait(driver, sec):
    return WebDriverWait(driver, sec)
#определяем функцию с ожиданиями, где возвращаем переменные драйвер и время

@pytest.fixture(scope="session")
def get_data():
    """Метод возвращает в тестовый класс Веб-элементы: информацию пользователя, таблицы с питомцами, даты для логирования"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=800,600')
    driver = webdriver.Chrome(options=chrome_options)
    # открывает страницу с помощью автоматизации через драйвер Chrome
    driver.get("https://petfriends.skillfactory.ru/")
    # нажимаем на кнопку "Зарегистрироваться", ждем 2 секунды, используем условие с неявным ожиданием элемента, то есть кнопки "Зарегистрироваться"
    driver.implicitly_wait(5)
    wait(driver, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[class$='btn-success']"))).click()
    # нажимаем на кнопку "У меня уже есть аккаунт", ждем 2 секунды
    wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@href='/login']"))).click()
    # вводим email, заданный в переменной, ждем 2 секунды
    input_email = wait(driver, 5).until(EC.presence_of_element_located((By.ID, 'email')))
    input_email.send_keys(email)
    # вводим пароль, заданный в переменной
    input_pass = driver.find_element(By.ID, "pass")
    input_pass.send_keys(password)
    # кликаем на вход в аккаунт с релеватными данными
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # открываем меню 
    try:
        a_menu = wait(driver, 5).\
            until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-toggle='collapse']")))
        a_menu.click()
    except ElementNotInteractableException:
        print("\nMenu is not found!")
        pass
    # кликаем по кнопке "Мои питомцы"  и ожидаем до тех пор, пока не произойдет появление и поиск элемента на странице
    my_pets = wait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/my_pets')]")))
    my_pets.click()
    # получаем информацию о зарегистрированном пользователе
    my_info = driver.find_elements(By.XPATH, "//div[contains(@class, 'left')]")
    # получаем таблицу с моими питомцами
    tr_table_my_pets = driver.find_elements(By.XPATH, "//tbody//tr")
    # вернем количество питомцев у пользователя и тело данных питомцев по строкам в таблице + время логирования
    data = datetime.datetime.now().strftime('%H_%M_%S')
    yield my_info, tr_table_my_pets, data
    driver.quit()
# опеределим класс для проведения тестов
class TestPetFriends():

    def test_equal_my_info_and_data_my_pets(self, get_data): #оперделяем функцию сравнения информации о количестве питомцев с данными в таблице
        my_info, tr_table_my_pets, date = get_data
        to_list_my_info = my_info[0].text.split("\n")
        # обозначаем, что информация в профиле моих питомцев равна количеству моих питомцев
        count_my_pets_in_my_info = to_list_my_info[1]
        # обрежем строку до ":" включительно, удалим пробельные символы, и преобразуем данные в целое число
        count_my_pets_in_my_info = int(
            count_my_pets_in_my_info[count_my_pets_in_my_info.find(":") + 1:].replace(" ", ""))
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_equal_my_info_and_data_my_pets.__name__}", file=file)
            print(f'Питомцев в инфо: {count_my_pets_in_my_info}\nв таблице: {len(tr_table_my_pets)}', file=file)
        # сверим всех питомцев
        assert count_my_pets_in_my_info == len(tr_table_my_pets)


    def test_only_half_without_photos(self, get_data): # определим функцию для питомцев с фото и без фото
        _, tr_table_my_pets, date = get_data
        # получим фото
        count_with_a_foto = 0
        count_without_photos = 0
        for item in tr_table_my_pets:
            if item.find_element(By.XPATH, "th//img").get_attribute('src') == "":
                count_without_photos += 1
            else:
                count_with_a_foto += 1
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_only_half_without_photos.__name__}", file=file)
            print(f"с фото = {count_with_a_foto}", f"без фото = {count_without_photos}", sep="\n", file=file)
        assert count_with_a_foto > count_without_photos

    def test_contains_name_age_breed(self, get_data): #определим функцию для всех питомцев, у которых есть имя, возраст и порода
        _, tr_table_my_pets, date = get_data
        contains_name_age_breed = True
        for i in range(len(tr_table_my_pets)): #используем цикл для определения длины
            if not contains_name_age_breed:
                break
            for j in range(1, 4):
                if tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text == "":
                    contains_name_age_breed = False
                    break
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(u"Тест: {}".format(self.test_contains_name_age_breed.__name__), file=file)
            print(u"У всех питомцев есть имя, возраст и порода = {}".format(contains_name_age_breed), file=file)

        assert contains_name_age_breed

    def test_all_names_are_different(self, get_data):  # Определим функцию для проверки разных имен у питомцев
        _, tr_table_my_pets, date = get_data
        all_names_are_different = True
        list_names = []
        for i in range(len(tr_table_my_pets)):
            name = tr_table_my_pets[i].find_element(By.XPATH, "td[1]").text
            if name in list_names:
                all_names_are_different = False
                break
            list_names.append(name)
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_all_names_are_different.__name__}", file=file)
            print(f"У всех питомцев разные имена = {all_names_are_different}", file=file)
        assert all_names_are_different

    def test_there_are_no_duplicate_pets_in_the_list(self, get_data): # определим функцию для проверки наличия повторяющихся питомцев в списке
        _, tr_table_my_pets, date = get_data
        there_are_no_duplicate_pets_in_the_list = True
        list_data = []
        # собираем данные каждого питомца в одну строку
        for i in range(len(tr_table_my_pets)):
            if not there_are_no_duplicate_pets_in_the_list:
                break
            string = tr_table_my_pets[i].find_element(By.XPATH, "th//img").get_attribute('src')
            for j in range(1, 4):
                string += tr_table_my_pets[i].find_element(By.XPATH, "td[{}]".format(j)).text
            hash_string = hashlib.md5(string.encode())
            hash_dig = hash_string.hexdigest()
            # если такой хэш уже есть, делаем флаг False, и break
            if hash_dig in list_data:
                there_are_no_duplicate_pets_in_the_list = False
                list_data.append(hash_dig)
                break
            list_data.append(hash_dig)
        # запишем результаты в файл
        with open(f"log{date}.txt", "a") as file:
            print("="*80, file=file)
            print(f"Тест: {self.test_there_are_no_duplicate_pets_in_the_list.__name__}", file=file)
            print(f"Нет повторяющихся питомцев. = {there_are_no_duplicate_pets_in_the_list}", file=file)
        assert there_are_no_duplicate_pets_in_the_list