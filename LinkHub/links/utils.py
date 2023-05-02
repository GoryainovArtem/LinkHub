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
    def wrapper(s):
        search_result = re.findall(pattern, s)
        return bool(search_result)
    return wrapper


image_pattern = r'<img'
video_pattern = r'<iframe'
find_image = closure(image_pattern)
find_youtube_video = closure(video_pattern)


# Для изображения
def count_image_percentage(lst):
    has_image_list = [find_image(i) for i in lst]
    return sum(has_image_list) / len(has_image_list)


# # Для видео
def count_video_percentage(lst):
    has_video_list = [find_youtube_video(link) for link in lst]
    return sum(has_video_list) / len(has_video_list)

def get_total_text_percentage(links_descriptions):
    text_percentage_list = [count_text_percentage(link) for link in links_descriptions]
    return (sum(map(lambda x: x[0], text_percentage_list)) /
            sum(map(lambda x: x[1], text_percentage_list))
            )


def get_project_statistic_field_value(links, instance, field_name: str, old_instance=None):
    links_documents = list(links.values_list(field_name, flat=True))
    if old_instance is not None:
        links_documents.remove(old_instance.description)
    links_documents.append(getattr(instance, field_name))
    filtered_links_documents = list(filter(None, links_documents))
    if len(links_documents) == 0:
        return 0
    return len(filtered_links_documents) / len(links_documents)
