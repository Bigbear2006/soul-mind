from core.choices import ExpertTypes

lunar_events = {
    '08.05.2023': {
        'event': 'Новолуние в Овне',
        'day_energy': 'Начало нового цикла, время для намерений',
    },
    '23.05.2023': {
        'event': 'Полнолуние в Стрельце',
        'day_energy': 'Расширение горизонтов, поиск истины',
    },
    '07.09.2023': {
        'event': 'Полное лунное затмение в Рыбах',
        'day_energy': 'Эмоциональное очищение, завершение циклов',
    },
    '21.09.2023': {
        'event': 'Частное солнечное затмение в Деве',
        'day_energy': 'Перезагрузка, переосмысление целей',
    },
    '06.10.2023': {
        'event': 'Новолуние в Весах',
        'day_energy': 'Баланс в отношениях, гармония',
    },
    '20.10.2023': {
        'event': 'Полнолуние в Овне',
        'day_energy': 'Действие, проявление лидерства',
    },
    '05.11.2023': {
        'event': 'Новолуние в Скорпионе',
        'day_energy': 'Трансформация, глубокие инсайты',
    },
    '19.11.2023': {
        'event': 'Полнолуние в Тельце',
        'day_energy': 'Материализация, стабильность',
    },
    '04.12.2023': {
        'event': 'Новолуние в Стрельце',
        'day_energy': 'Оптимизм, планирование будущего',
    },
    '19.12.2023': {
        'event': 'Полнолуние в Близнецах',
        'day_energy': 'Коммуникация, обмен идеями',
    },
}

planetary_alignments = {
    '24.05.2023': {
        'event': 'Соединение Меркурия и Урана',
        'day_energy': 'Внезапные инсайты, нестандартное мышление',
    },
    '29.08.2023': {
        'event': 'Планетарное выравнивание (6 планет)',
        'day_energy': 'Гармонизация, синхронизация с космосом',
    },
    '06.10.2023': {
        'event': 'Соединение Венеры и Марса',
        'day_energy': 'Страсть, баланс мужской и женской энергии',
    },
}

power_calendar = (
    '🌑 Лунные фазы и затмения\n'
    'Дата\tСобытие\tЭнергия дня\n'
    '8 мая\tНоволуние в Овне\tНачало нового цикла, время для намерений\n'
    '23 мая\tПолнолуние в Стрельце\tРасширение горизонтов, поиск истины\n'
    '7 сентября\tПолное лунное затмение в Рыбах\tЭмоциональное очищение, завершение циклов\n'
    '21 сентября\tЧастное солнечное затмение в Деве\tПерезагрузка, переосмысление целей\n'
    '6 октября\tНоволуние в Весах\tБаланс в отношениях, гармония\n'
    '20 октября\tПолнолуние в Овне\tДействие, проявление лидерства\n'
    '5 ноября\tНоволуние в Скорпионе\tТрансформация, глубокие инсайты\n'
    '19 ноября\tПолнолуние в Тельце\tМатериализация, стабильность\n'
    '4 декабря\tНоволуние в Стрельце\tОптимизм, планирование будущего\n'
    '19 декабря\tПолнолуние в Близнецах\tКоммуникация, обмен идеями\n\n'
    '🪐 Планетарные соединения и выравнивания\n'
    'Дата\tСобытие\tЭнергия дня\n'
    '24 мая\tСоединение Меркурия и Урана\tВнезапные инсайты, нестандартное мышление\n'
    '29 августа\tПланетарное выравнивание (6 планет)\tГармонизация, синхронизация с космосом\n'
    '6 октября\tСоединение Венеры и Марса\tСтрасть, баланс мужской и женской энергии\n\n'
    '🔁 Ретроградные периоды\n'
    'Период\tПланета\tЭнергия периода\n'
    '17 июня – 11 июля\tМеркурий\tПересмотр коммуникаций, осторожность в делах\n'
    '1 сентября – 3 октября\tВенера\tПереоценка ценностей, отношений\n'
    '10 ноября – 2 декабря\tМарс\tЗамедление действий, переосмысление целей'
)

personal_report_intro = (
    'SoulMind — пространство, где ты встречаешь себя\n\n'
    'Этот отчёт — не инструкция.\n'
    'И не обещание «счастья по пунктам».\n'
    'Это встреча.\n\n'
    'С собой настоящим. С энергией, которая течёт в тебе.\n'
    'С голосом, который ты когда-то перестал слушать — но он остался.\n\n'
    'Soul Muse не говорит «как надо».\n'
    'Она говорит от имени той части тебя, которая всегда знала.\n\n'
    'Прочитай это не глазами. А вниманием.\n'
    'Послушай не только то, что сказано. А то, что оживает между строк.\n\n'
    'Ты здесь — и ты готов.\n\n\n'
)

personal_report_audio_closures = [
    'Всё, что тебе нужно, уже внутри.\nЯ просто разбудила тебя. Остальное — ты уже знаешь.',
    'Слова заканчиваются. Но движение только начинается.\nТвоя энергия знает путь. Доверься ей.',
    'Если сердце стало тише — не бойся.\nЭто значит, ты наконец услышал.',
    'Уходи отсюда не с планом, а с чувствами.\nЭто они приведут тебя туда, куда ты пришёл.',
    'Ты можешь сомневаться в любом совете.\nНо не в себе. Себя ты теперь знаешь лучше.',
    'Если ты что-то почувствовал — значит, отчёт уже сработал.\nВстретился с собой? Я — рядом.',
    'Я замолкаю. Но ты продолжай.\nПотому что этот месяц — о тебе. Не обо мне.',
]

mosaic_intros = [
    'Ты прошёл уже не один шаг. Это слышно. Это чувствуется. И это не случайно.',
    'С каждым голосом ты всё больше вспоминаешь. Не узнаешь — а вспоминаешь. Себя.',
    'Ты говорил, ты слушал, ты задавал. А теперь просто будь. И слушай меня.',
]

mosaic_experts_texts = {
    ExpertTypes.ASTROLOGIST: (
        'Ты слушал голос звёзд. Они не приказывают — они напоминают. О ритме. О цикле. О предназначении.'
    ),
    ExpertTypes.NUMEROLOGIST: (
        'Ты заглянул в структуру своей души — через числа. Ты почувствовал, что порядок может быть мистическим.'
    ),
    ExpertTypes.PSYCHOLOGIST: (
        'Ты отважился взглянуть внутрь. В теневые уголки, в раненые части. Это требует мужества. Ты это сделал.'
    ),
    ExpertTypes.HD_ANALYST: (
        'Ты встретился со своей механикой. Со своей энергией. Не чтобы исправить, а чтобы принять.'
    ),
    ExpertTypes.SPIRITUAL_MENTOR: (
        'Ты слушал интуицию. Свою, не чужую. Через голос, который говорил мягко, но глубоко.'
    ),
}

mosaic_topic_texts = {
    'Отношения': 'Ты спрашивал про любовь, про связь, про боль в близости. Это про тебя. И про них. И про рост.',
    'Предназначение': 'Ты не просто хочешь жить — ты хочешь смысл. И ты ищешь его с честностью.',
    'Эмоции': 'Ты позволил себе чувствовать. И это уже целительство. Потому что притворство — не твой путь.',
    'Деньги': 'Ты учишься принимать. Не только чувства, но и изобилие. Это про ценность. Про тебя.',
    'Принятие себя': 'Ты смотришь в зеркало, не чтобы оценить. А чтобы признать. Без маски. Без страха.',
    'Страхи и сомнения': 'Ты коснулся страха. Но не отступил. Это уже победа. Не внешняя — внутренняя.',
    'Интуиция': 'Ты слушал не ум. Ты слушал чутьё. Это и есть взросление души.',
    'Здоровье': 'Ты не просто тело. Но ты и тело. Ты ищешь баланс. Между видимым и неявным.',
    'Карьера': 'Ты спрашивал про дело, но за этим — всегда вопрос: кто я? И зачем?',
    'Детство и травмы': 'Ты вернулся туда, где всё началось. Чтобы наконец — выбрать себя.',
    'Семья и род': 'Ты несёшь то, что было до тебя. И учишься — нести иначе.',
    'Энергия': 'Ты чувствовал себя опустошённым. И начал искать, что наполняет по-настоящему.',
    'Циклы жизни': 'Ты идёшь через перемены. Ты уже не прежний. И это прекрасно.',
    'Духовный путь': 'Ты слушал, что не уловить словами. И доверился этому.',
    'Выбор / раздор внутри': 'Ты был на распутье. И начал выбирать не из страха. А из себя.',
}

mosaic_endings = [
    'Ты уже идёшь. И то, что ты ищешь — не снаружи. Оно уже внутри. Я просто напомнила.',
    'Ты не сломан. Ты в переходе. Я рядом, когда ты захочешь снова услышать.',
    'Ты просыпаешься. Не внезапно. Но неотвратимо. Это красиво.',
    'Ты услышал себя в разных отражениях. Теперь — собирай. Не спеши. Просто помни.',
    'Иди глубже. Не потому что надо. А потому что можешь. И это делает тебя свободным.',
]

ask_question_instructions = (
    '— «Вопрос — это не просто слова. Это как зеркало. Чем яснее ты сформулируешь, '
    'тем точнее голос найдёт путь. Вот три подсказки от меня...»\n'
    '1. Будь конкретен. Вместо «что мне делать?» скажи: '
    '«я застрял в отношениях и не понимаю, это страх или правда?»\n'
    '2. Говори голосом, если можешь. В твоей интонации больше правды, чем ты думаешь.\n'
    '3. Если не знаешь, как спросить — просто скажи это. Это уже начало. И это нормально.\n'
    'Soul Muse — не судит. Она слышит. И помогает видеть, что внутри уже есть ответ.'
)
