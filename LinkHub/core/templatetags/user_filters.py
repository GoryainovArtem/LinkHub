from django import template

from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


@register.filter
def get_description(text):
    soup = BeautifulSoup(text, features='html.parser')
    all_text = soup.get_text()
    print(type(all_text))
    print(all_text)
    displayed_part = max(all_text.split('\n'), key=len)[:120]
    result_text = ('... ' + displayed_part[0].lower() +
                   displayed_part[1:] + ' ...')
    return result_text
