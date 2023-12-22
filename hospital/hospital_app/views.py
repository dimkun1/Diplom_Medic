from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.utils import timezone
from django.db.models import Q
from users.models import User
from datetime import timedelta
from .models import Appointment
from .forms import PatientNewAppointmentForm, DoctorAnswerForm




def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


class HomeView(View):
    template_name = 'hospital_app/home.html'

    def get(self, request, *args, **kwargs):
        context = ({
            'title': 'Медик',
        })
        return render(request, self.template_name, context=context)


class ContactView(View):
    template_name = 'hospital_app/home_contact.html'

    def get(self, request, *args, **kwargs):
        context = ({
            'title': 'Контакты',
        })
        return render(request, self.template_name, context=context)


class AwardsView(View):
    template_name = 'hospital_app/home_awards.html'

    def get(self, request, *args, **kwargs):
        context = ({
            'title': 'Награды',
        })
        return render(request, self.template_name, context=context)


# список всех докторов
class DoctorListView(ListView):
    model = User
    template_name = 'hospital_app/doctors_all.html'
    context_object_name = 'doctors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Наш персонал',
        })
        return context

    def get_queryset(self):
        # Получаем докторов из группы Doctors

        return User.objects.filter(groups__name='Doctors')


# новая заявка пациента
class PatientNewAppointmentView(UserPassesTestMixin, CreateView):
    model = Appointment
    form_class = PatientNewAppointmentForm
    template_name = 'hospital_app/patient_appointment_new.html'
    context_object_name = 'appointment'
    success_url = reverse_lazy('patient_appointment_new')

    def test_func(self):
        # Проверяем, принадлежит ли текущий пользователь к нужной группе
        # return self.request.user.groups.filter(name='Patient').exists()
        allowed_groups = ['Patient', 'staff', 'root']
        return self.request.user.groups.filter(name__in=allowed_groups).exists()

    def handle_no_permission(self):
        # Перенаправляем пользователя на домашнюю страницу
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Новое обращение',
        })
        return context

    def form_valid(self, form):
        # Устанавливаем пациента перед сохранением формы
        form.instance.patient = self.request.user

        if form.instance.start_date_time < timezone.now():
            messages.error(self.request, 'Дата начала приёма не может быть в прошлом.')
            return self.form_invalid(form)

        # end_date_time = form.cleaned_data.get('end_date_time')
        end_date_time = form.instance.start_date_time + timedelta(minutes=30)

        conflicting_appointments_patient = Appointment.objects.filter(
            patient=form.instance.patient,
            start_date_time__lte=end_date_time,
            end_date_time__gte=form.instance.start_date_time
        )

        if conflicting_appointments_patient.exists():
            messages.error(self.request, 'У вас есть запись в это время.')
            return self.form_invalid(form)

        end_date_time = form.instance.start_date_time + timedelta(minutes=30)

        conflicting_appointments_doctor = Appointment.objects.filter(
            doctor=form.instance.doctor,
            start_date_time__lte=end_date_time,
            end_date_time__gte=form.instance.start_date_time
        )

        if conflicting_appointments_doctor.exists():
            messages.error(self.request, 'В это время у доктора уже есть приём, выбирете другое время.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        messages.success(self.request, 'Запись успешно создана.')  # Сообщение об успешном создании записи
        return response

    def get_form_kwargs(self):
        # Передаем request в форму через параметр request
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


# ответ доктора
class DoctorAnswerView(UserPassesTestMixin, UpdateView):
    model = Appointment
    form_class = DoctorAnswerForm
    template_name = 'hospital_app/doctor_answer.html'
    context_object_name = 'appointment'
    success_url = reverse_lazy('doctor_answer')

    def test_func(self):
        # Проверяем, принадлежит ли текущий пользователь к нужной группе
        # return self.request.user.groups.filter(name='Doctors').exists()
        allowed_groups = ['Doctors', 'staff', 'root']
        return self.request.user.groups.filter(name__in=allowed_groups).exists()

    def handle_no_permission(self):
        # Перенаправляем пользователя на домашнюю страницу
        return redirect('home')

    def get_object(self, queryset=None):
        # Возвращает объект Appointment на основе переданного appointment_id из URL
        return Appointment.objects.get(pk=self.kwargs['appointment_id'])

    def form_valid(self, form):
        # Устанавливаем doctor перед сохранением формы
        # form.instance.doctor = self.request.user

        # Ваша логика обработки формы
        response = super().form_valid(form)

        messages.success(self.request, 'Запись успешно создана.')  # Сообщение об успешном создании записи
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Ответ Доктора',
        })
        return context

    def get_success_url(self):
        # Получаем значение appointment_id из формы после её сохранения
        appointment_id = self.object.id
        # Используем его для генерации URL с параметром appointment_id
        return reverse('doctor_answer', args=[appointment_id])

    def get_form_kwargs(self):
        # Передаем request и appointment_id в форму через параметр request и appointment_id
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        kwargs['appointment_id'] = self.kwargs['appointment_id']

        # Получаем имя пациента из объекта Appointment или из request.user
        appointment = self.get_object()
        kwargs[
            'patient_name'] = appointment.patient.get_full_name() if appointment else self.request.user.get_full_name()
        kwargs['doctor_name'] = appointment.doctor.get_full_name() if appointment else self.request.user.get_full_name()

        return kwargs


# список новых заявко пациента
class PatientNewListView(UserPassesTestMixin, ListView):
    model = Appointment
    template_name = 'hospital_app/patient_history_new.html'  # Путь к вашему шаблону
    context_object_name = 'appointment'

    def test_func(self):
        # Проверяем, принадлежит ли текущий пользователь к нужной группе
        # return self.request.user.groups.filter(name='Patient').exists()
        allowed_groups = ['Patient', 'staff', 'root']
        return self.request.user.groups.filter(name__in=allowed_groups).exists()

    def handle_no_permission(self):
        # Перенаправляем пользователя на домашнюю страницу
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Новые обращения',
        })
        return context

    def get_queryset(self):
        # Получаем текущего аутентифицированного пользователя
        user = self.request.user

        # Фильтруем записи по полю 'patient'
        queryset = Appointment.objects.filter(Q(patient=user) & Q(readings__exact='')).order_by('-start_date_time')
        return queryset


# список старых заявко пациента
class PatientOldListView(UserPassesTestMixin, ListView):
    model = Appointment
    template_name = 'hospital_app/patient_history_old.html'  # Путь к вашему шаблону
    context_object_name = 'appointment'

    def test_func(self):
        # Проверяем, принадлежит ли текущий пользователь к нужной группе
        # return self.request.user.groups.filter(name='Patient').exists()
        allowed_groups = ['Patient', 'staff', 'root']
        return self.request.user.groups.filter(name__in=allowed_groups).exists()

    def handle_no_permission(self):
        # Перенаправляем пользователя на домашнюю страницу
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Старые обращения',
        })
        return context

    def get_queryset(self):
        # Получаем текущего аутентифицированного пользователя
        user = self.request.user

        # Фильтруем записи по полю 'patient'
        queryset = Appointment.objects.filter(Q(patient=user) & Q(readings__gt='')).order_by('-start_date_time')

        return queryset


# список не отвеченых заявок для доктора
class DoctorHistoryListView(UserPassesTestMixin, ListView):
    model = Appointment
    template_name = 'hospital_app/doctor_history.html'  # Путь к вашему шаблону
    context_object_name = 'appointment'

    def test_func(self):
        # Проверяем, принадлежит ли текущий пользователь к нужной группе
        # return self.request.user.groups.filter(name='Doctors').exists()
        allowed_groups = ['Doctors', 'staff', 'root']
        return self.request.user.groups.filter(name__in=allowed_groups).exists()

    def handle_no_permission(self):
        # Перенаправляем пользователя на домашнюю страницу
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Ожидают ответа',
        })
        return context

    def get_queryset(self):
        # Получаем текущего аутентифицированного пользователя
        user = self.request.user

        # Фильтруем записи по полю 'patient'

        queryset = Appointment.objects.filter(Q(doctor=user) & Q(readings__exact='')).order_by('-start_date_time')
        print(queryset)
        return queryset


# список всех овтетов доктора
class DoctorAllHistoryListView(UserPassesTestMixin, ListView):
    model = Appointment
    template_name = 'hospital_app/doctor_history_all.html'  # Путь к вашему шаблону
    context_object_name = 'appointment'

    def test_func(self):
        # Проверяем, принадлежит ли текущий пользователь к нужной группе
        # return self.request.user.groups.filter(name='Doctors').exists()
        allowed_groups = ['Doctors', 'staff', 'root']
        return self.request.user.groups.filter(name__in=allowed_groups).exists()

    def handle_no_permission(self):
        # Перенаправляем пользователя на домашнюю страницу
        return redirect('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Ваши ответы',
        })
        return context

    def get_queryset(self):
        # Получаем текущего аутентифицированного пользователя
        user = self.request.user

        # Фильтруем записи по полю 'doctor'
        queryset = Appointment.objects.filter(Q(doctor=user) & Q(readings__gt='')).order_by('-start_date_time')
        print(queryset)
        return queryset


class TagsAnalizeView(View):
    template_name = 'hospital_app/tags_analyzes.html'

    def get(self, request, *args, **kwargs):
        context = ({
            'title': 'Анализы',
        })
        return render(request, self.template_name, context=context)


class TagsMrtView(View):
    template_name = 'hospital_app/tags_mrt.html'

    def get(self, request, *args, **kwargs):
        context = ({
            'title': 'МРТ',
        })
        return render(request, self.template_name, context=context)


class TagsKtView(View):
    template_name = 'hospital_app/tags_kt.html'

    def get(self, request, *args, **kwargs):
        context = ({
            'title': 'КТ',
        })
        return render(request, self.template_name, context=context)
