from aiogram.fsm.state import State, StatesGroup


class UserInfoState(StatesGroup):
    gender = State()
    fullname = State()
    birth_date = State()
    birth_time = State()
    birth_location = State()


class CompatabilityEnergyState(StatesGroup):
    connection_type = State()
    birth_date_2 = State()


class SoulMuseQuestionState(StatesGroup):
    question = State()


class VIPCompatabilityState(StatesGroup):
    payment_type = State()
    payment = State()
    fullname = State()
    birth_date = State()
    birth_time = State()
    birth_location = State()
    report = State()
