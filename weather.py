# -*- coding: utf-8 -*-
from config import INTENTS, SCENARIOS
import handlers


class UserState:
    """
    class to keep context to exchange between handlers, and current scenario step
    """
    def __init__(self):
        self.scenario_name = None
        self.step = None
        self.context = {}


def available_intents() -> str:
    """
    return string with available intents from config.INTENTS
    @return: str
    """
    result = '\n'
    for key, intent in INTENTS.items():
        result += f"{key}: {intent['name']}\n"
    result += "0: Выход\n>>> "
    return result


if __name__ == '__main__':
    user_state = UserState()
    is_stopped = False
    while not is_stopped:
        if user_state.scenario_name is None:
            intents = available_intents()
            user_choose = input(intents)
            if user_choose == '0':
                is_stopped = True
            elif user_choose in INTENTS:
                user_state.scenario_name = INTENTS[user_choose]['scenario_name']
                user_state.step_name = 'step1'
            else:
                print(f'Элемент с номером "{user_choose}" не найден! Попробуйте еще раз.\n')
        else:
            current_step = SCENARIOS[user_state.scenario_name][user_state.step_name]
            handler_name = current_step['handler']
            message = current_step['message']
            handler = getattr(handlers, handler_name)
            if current_step['input_required']:
                user_input = input(message + "\n>>> ")
            else:
                user_input = None
            result = handler(user_input, user_state.context)
            if result:
                next_step = current_step['next_step']
                if next_step:
                    user_state.step_name = next_step
                else:
                    user_state.scenario_name = None
                    user_state.step_name = None
                continue

            failure_message = current_step['failure']
            print(failure_message)
