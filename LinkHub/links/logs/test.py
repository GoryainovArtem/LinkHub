import re
# lst = [1, 5, 4, 3, 5, 3, 4, 2, 2, 1, 1, 1, 1, 7]
#
#
# def find_most_appear_themes(lst):
#     data = list(map(lambda x: (x, lst.count(x)), set(lst)))
#     data.sort(key=lambda x: x[1])
#     return list(map(lambda x: x[0], data))[:3]
#
#
# def add_coefficients(my_projects_list, liked_projects_list,
#                      saved_projects_list, watched_project_list):
#     my_project_coef = 3
#     liked_project_coef = 1.5
#     saved_project_coef = 1
#     watched_project_coef = 0.75
#     my_project_coefs_list = [my_project_coef] * len(my_projects_list)
#     liked_project_coefs_list = [liked_project_coef] * len(liked_projects_list)
#     saved_project_coefs_list = [saved_project_coef] * len(saved_projects_list)
#     watched_project_coefs_list = [watched_project_coef] * len(watched_project_list)
#     return (list(zip(my_projects_list, my_project_coefs_list)) +
#             list(zip(liked_projects_list, liked_project_coefs_list)) +
#             list(zip(saved_projects_list, saved_project_coefs_list)) +
#             list(zip(watched_project_list, watched_project_coefs_list)))
#
#
# lst = add_coefficients(lst, lst, lst, lst)
# print(lst)
#
# example = [(1, 3), (5, 3), (4, 3), (3, 3), (5, 3), (3, 3), (4, 3), (2, 3), (2, 3), (1, 3), (1, 3), (1, 3), (1, 3),
#            (7, 3), (1, 1.5), (5, 1.5), (4, 1.5), (3, 1.5), (5, 1.5), (3, 1.5), (4, 1.5), (2, 1.5), (2, 1.5), (1, 1.5),
#            (1, 1.5), (1, 1.5), (1, 1.5), (7, 1.5), (1, 1), (5, 1), (4, 1), (3, 1), (5, 1), (3, 1), (4, 1), (2, 1),
#            (2, 1), (1, 1), (1, 1), (1, 1), (1, 1), (7, 1), (1, 0.75), (5, 0.75), (4, 0.75), (3, 0.75), (5, 0.75),
#            (3, 0.75), (4, 0.75), (2, 0.75), (2, 0.75), (1, 0.75), (1, 0.75), (1, 0.75), (1, 0.75), (7, 0.75)]
#
# tags_coefficients = {}
# for i in example:
#     tags_coefficients.setdefault(i[0], 0)
#     tags_coefficients[i[0]] += i[1]
# print(tags_coefficients)

#
# lst_1 = [(7, 3), (2, 3), (3, 3)]
# lst_2 = [(7, 3), (2, 3), (3, 3)]
# lst_3 = [(7, 3), (2, 3), (3, 3)]
#
# all_themes_list = []
# for i in (lst_1, lst_2, lst_3):
#     all_themes_list.extend(lst)
#
# print(all_themes_list)



# post_text = """
# <p><iframe allowfullscreen="" frameborder="0" height="360" src="https://www.youtube.com/embed/Z5eqkXG773s" width="640"></iframe><br />
# Норм курс, но я бы больше не купил. Дороговато для базы, а так в целом нелохо</p>
#
# <p><img alt="" src="/media/uploads/2023/04/05/ava_voqyHcE.jpg" style="height:300px; width:300px" /></p>
# """
#
#
# def find_text_percent(s):
#     pattern = r'''(>|\n)([А-Яа-я\w0-9 ,.!?'"@=]+)<'''
#     text = re.findall(pattern, s)
#     if text:
#         return len(''.join(map(lambda x: x[1], text))) / len(s)
#     else:
#         return 0
#
#
# s = """
# <p><iframe allowfullscreen="" frameborder="0" height="360" src="https://www.youtube.com/embed/Z5eqkXG773s" width="640"></iframe><br />
# Норм курс, но я бы больше не купил. Дороговато для базы, а так в целом нелохо</p>
#
# <p><img alt="" src="/media/uploads/2023/04/05/ava_voqyHcE.jpg" style="height:300px; width:300px" /></p>
# <p>Знатное вложение денег. Можно начать учиться в любое время. За это МЕГА респект</p>
# """
# print(find_text_percent(s))
#
#
# def closure(pattern):
#     def wrapper():
#         search_result = re.findall(pattern, s)
#         return bool(search_result)
#     return wrapper
#
#
# image_pattern = r'<img'
# video_pattern = r'<iframe'
# find_image = closure(image_pattern)
# find_youtube_video = closure(video_pattern)

# # Просмотренные страницы
# import re
# import pandas as pd
# with open('D:/Dev/LinkHub/LinkHub/logs/pages/2.log') as file:
#     pattern = r'., DEBUG,'
#     data = [line.strip('\n') for line in file.readlines()]
#     data = [line for line in data if re.search(pattern, line)]
#     print(*data, sep='\n')
#
#     data = list(map(lambda x: x.split(', '), data))
#     data = [i for i in data if i[2] == 'root']
#     df = pd.DataFrame(data, columns=['date', 'level', 'user', 'project_id'])
#     res = df.groupby(by='project_id').date.count().nlargest(2)
#     watched_projects_ids = list(map(int, res.keys()))



from bs4 import BeautifulSoup


html = """
dhdhdhdhd ahahahhaha nete net<img alt="" src="https://mobimg.b-cdn.net/v3/fetch/b5/b59cb84829d07b33035b671f69184a61.jpeg" style="height:125px; width:200px" />&nbsp;ВОООООТ хыч хыч ваномас&nbsp;&nbsp;<img alt="" src="https://mobimg.b-cdn.net/v3/fetch/a2/a253c5869732a1cbabf74443e1467efd.jpeg?w=1470&amp;r=0.5625" style="height:394px; width:700px" />&nbsp;рята тта<br />
<br />
афупфп а
<p><br />
&nbsp;</p>

<table border="1" cellpadding="1" cellspacing="1" style="width:500px">
	<tbody>
		<tr>
			<td>hfg</td>
			<td>h</td>
		</tr>
		<tr>
			<td>hh</td>
			<td>h</td>
		</tr>
		<tr>
			<td>h</td>
			<td>h</td>
		</tr>
	</tbody>
</table>

<p><br />
&nbsp;</p>

<blockquote>
<p>,gfhgfh fjfg j f&nbsp; fj fjfjfjfj<br />
hfghh</p>
</blockquote>
<br />
<iframe frameborder="0" height="360" src="https://www.youtube.com/embed/umRGf1CMhxs?start=0" width="640"></iframe>
"""
soup = BeautifulSoup(html, features="html.parser")

# get text
text = soup.get_text()
res = ''.join(text.split())

print(res)



