from django import template

from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def addclass(field, css):
    """Добавить CSS стиль для выбранного тега."""
    return field.as_widget(attrs={'class': css})


@register.filter
def get_description(text):
    """Форматировать выводимое описание проекта/раздела/источника:
    определить самый большой текстовый блок описания. Максимальная длина
    120 символов.
    """
    soup = BeautifulSoup(text, features='html.parser')
    all_text = soup.get_text()
    print(type(all_text))
    print(all_text)
    phrase_list = all_text.split('\n')
    displayed_part = max(phrase_list, key=len)
    if displayed_part == phrase_list[0]:
        result_text = displayed_part
    else:
        result_text = ('... ' + displayed_part[0].lower() +
                       displayed_part[1:])
    if len(result_text) >= 120:
        result_text = result_text[:120] + ' ...'
    return result_text
