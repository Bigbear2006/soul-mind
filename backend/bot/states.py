from aiogram.fsm.state import State, StatesGroup


class UserInfoState(StatesGroup):
    gender = State()
    birth_datetime = State()
    birth_location = State()
