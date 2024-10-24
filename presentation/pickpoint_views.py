def score_comment_view(score: int) -> str:
    if score < 4:
        comment = 'Напишите, пожалуйста, что именно Ваc не устроило.'
    else:
        comment = 'Напишите, пожалуйста, что именно Вам понравилось.'
    return (f'Вы поставили оценку <strong>{score}</strong>.\n'
            f'{comment}\n'
            f'Обратите внимание, что комментарий является <strong>обязательным</strong>.')


def set_score_view(pp_name: str) -> str:
    return f'Вы выбрали пункт выдачи: <b>{pp_name}</b>\nПоставьте оценку от <b>1</b> до <b>5</b>:'
