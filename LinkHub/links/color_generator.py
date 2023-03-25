def color_generator(amount: int) -> list:
    """
    Сгенерировать последовательность из номеров
    случайных цветов
    :param amount:
    :return:
    """
    # Оранжевый, зеленый, красный, синий
    colors_list = [
        '#FF8C00',
        '#32CD32',
        '#FF0000',
        '#0000FF'
    ]
    from random import randint
    random_color_list = [colors_list[randint(0, len(colors_list))] for _ in range(amount)]
    return random_color_list