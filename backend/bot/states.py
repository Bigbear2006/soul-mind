from aiogram.fsm.state import State, StatesGroup


class UserInfoState(StatesGroup):
    gender = State()
    fullname = State()
    birth_date = State()
    birth_time = State()
    birth_location = State()
    email = State()


class CompatabilityEnergyState(StatesGroup):
    payment_type = State()
    payment = State()
    connection_type = State()
    birth_date_2 = State()


class SoulMuseQuestionState(StatesGroup):
    payment_type = State()
    payment = State()
    question = State()


class VIPCompatabilityState(StatesGroup):
    payment_type = State()
    payment = State()
    fullname = State()
    birth_date = State()
    birth_time = State()
    birth_location = State()
    report = State()


class PersonalReportState(StatesGroup):
    payment_type = State()
    payment = State()


class MiniConsultState(StatesGroup):
    payment_type = State()
    payment = State()
    intention = State()
    topics = State()
    photo = State()  # only for ExpertTypes.SPIRITUAL_MENTOR
    question = State()
    answer_consult = State()
    comment = State()


class FridayGiftState(StatesGroup):
    insight = State()
