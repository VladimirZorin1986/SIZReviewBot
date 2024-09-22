def switch_start_cancel_view(message_text: str, is_auth: bool) -> str:
    match (message_text, is_auth):
        case ('/start', True):
            return 'Теперь вы можете оценить выдачу СИЗ'
        case ('/start', False):
            return 'Для продолжения работы необходимо авторизоваться. При авторизации Вы соглашаетесь с обработкой ваших персональных данных (номер телефона) с целью оценки выдачи СИЗ в ГК "ОТЭКО".'
        case ('/cancel', True):
            return 'Действие отменено. Возврат в главное меню'
        case ('/cancel', False):
            return 'Действие отменено. Вы не авторизованы в системе'
