from django import template

register = template.Library()

menu = [{'title': "Наши достижения", 'url_name': 'awards'},
        {'title': "Наш персонал", 'url_name': 'doctors_all'},
        {'title': "Наши контакты", 'url_name': 'contact'},
        ]


@register.simple_tag
def get_menu():
    return menu


menu_left = [{'title': "Анализы", 'url_name': 'analyzes'},
             {'title': "Мрт", 'url_name': 'mrt'},
             {'title': "КТ", 'url_name': 'kt'}
             ]


@register.simple_tag
def get_menu_left():
    return menu_left


menu_patient = [{'title': "Новые обращения", 'url_name': 'patient_history_new'},
                {'title': "Старые обращение", 'url_name': 'patient_history_old'},
                {'title': "Новая запись", 'url_name': 'patient_appointment_new'},
                ]


@register.simple_tag
def get_menu_patient():
    return menu_patient


menu_doctor = [{'title': "Ответить пациенту", 'url_name': 'doctor_history'},
               {'title': "История ответов", 'url_name': 'doctor_history_all'},
               ]


@register.simple_tag
def get_menu_doctor():
    return menu_doctor
