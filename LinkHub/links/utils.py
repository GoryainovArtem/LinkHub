import re

from bs4 import BeautifulSoup


def count_text_percentage(s: str):
    """Вычислить количество текста в источнике."""
    soup = BeautifulSoup(s, features="html.parser")
    text = soup.get_text()
    text = ''.join(text.split())
    if text:
        return len(text), len(s)
    else:
        return 0, 0


def closure(pattern):
    """
    Замыкание для поиска в тексте описания источника
    информации заданного паттерна.
    :param pattern:
    :return:
    """
    def wrapper(s):
        search_result = re.findall(pattern, s)
        return bool(search_result)
    return wrapper


image_pattern = r'<img'
video_pattern = r'<iframe'
find_image = closure(image_pattern)
find_youtube_video = closure(video_pattern)


def count_image_percentage(lst):
    """
    Определить в какой части источников информации
    проекта присутствует хотя бы одно изображение.
    :param lst:
    :return:
    """
    has_image_list = [find_image(i) for i in lst]
    return sum(has_image_list) / len(has_image_list)


def count_video_percentage(lst):
    """
    Определить в какой части источников информации
    проекта присутствует хотя бы одно видео.
    :param lst:
    :return:
    """
    has_video_list = [find_youtube_video(link) for link in lst]
    return sum(has_video_list) / len(has_video_list)


def get_total_text_percentage(links_descriptions):
    """
    Определить общий процент текста во всех описаниях источников
    информации проекта.
    :param links_descriptions:
    :return:
    """
    text_percentage_list = [count_text_percentage(link) for link in links_descriptions]
    return (sum(map(lambda x: x[0], text_percentage_list)) /
            sum(map(lambda x: x[1], text_percentage_list))
            )


def get_project_statistic_field_value(links, instance, field_name: str, old_instance=None):
    """
    Определить значение статистического поля таблицы Project
    :param links:
    :param instance:
    :param field_name:
    :param old_instance:
    :return:
    """
    field_values_list = list(links.values_list(field_name, flat=True))
    if old_instance is not None:
        field_values_list.remove(old_instance.description)
    field_values_list.append(getattr(instance, field_name))
    filtered_links_documents = list(filter(None, field_values_list))
    if len(field_values_list) == 0:
        return 0
    return len(filtered_links_documents) / len(field_values_list)
