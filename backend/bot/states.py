from aiogram.fsm.state import State, StatesGroup


class UserInfoState(StatesGroup):
    gender = State()
    fullname = State()
    birth_date = State()
    birth_time = State()
    birth_location = State()
