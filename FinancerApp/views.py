from itertools import chain

from django.contrib import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models.functions import TruncMonth, TruncYear, TruncDay
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from FinancerApp.forms import SignUpForm, IncomeForm, ExpenseForm
from FinancerApp.models import Income, Expense
from collections import defaultdict

# Create your views here.
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'FinancerApp/login.html', {'form': form})
def register_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')  # Use password1 for the password field
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('profile')
    else:
        form = SignUpForm()
    return render(request, 'FinancerApp/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

# @login_required(login_url='login')
# def main_view(request):
#     incomes_per_day = Income.objects.filter(user=request.user).values('date').annotate(total_amount=Sum('amount'))
#     expenses_per_day = Expense.objects.filter(user=request.user).values('date').annotate(total_amount=Sum('amount'))
#
#     # Создаем словарь, в котором ключами будут даты, а значениями будут суммы доходов и расходов за каждый день
#     transactions_per_day = {}
#     for income in incomes_per_day:
#         transactions_per_day[income['date']] = {'income': income['total_amount'], 'expense': 0}
#
#     for expense in expenses_per_day:
#         if expense['date'] in transactions_per_day:
#             transactions_per_day[expense['date']]['expense'] = expense['total_amount']
#         else:
#             transactions_per_day[expense['date']] = {'income': 0, 'expense': expense['total_amount']}
#
#     return render(request, 'FinancerApp/index.html', {'transactions_per_day': transactions_per_day})

@login_required(login_url='login')
def profile(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            transactions_history = get_transactions_history(request.user)

            transactions_per_month = get_transactions_per_month(request.user)
            transactions_per_day = get_transactions_per_day(request.user)
            transactions_per_year = get_transactions_per_year(request.user)

        elif request.method == 'POST':
            if 'toggle' in request.POST:
                if request.POST['toggle'] == 'month':
                    transactions_per_month = get_transactions_per_month(request.user)
                    transactions_per_day = get_transactions_per_day(request.user)
                    transactions_per_year = get_transactions_per_year(request.user)
                elif request.POST['toggle'] == 'day':
                    transactions_per_day = get_transactions_per_day(request.user)
                    transactions_per_month = None
                    transactions_per_year = None

        return render(request, 'FinancerApp/profile.html', {
            'transactions_per_month': transactions_per_month,
            'transactions_per_day': transactions_per_day,
            'transactions_per_year': transactions_per_year,
            'transactions_history': transactions_history
        })
    else:
        return redirect('login')

def get_transactions_per_month(user):
    incomes_per_month = Income.objects.filter(user=user).annotate(month=TruncMonth('date')).values('month').annotate(total_amount=Sum('amount'))
    expenses_per_month = Expense.objects.filter(user=user).annotate(month=TruncMonth('date')).values('month').annotate(total_amount=Sum('amount'))

    transactions_per_month = {}
    for income in incomes_per_month:
        transactions_per_month[income['month']] = {'income': income['total_amount'], 'expense': 0}

    for expense in expenses_per_month:
        if expense['month'] in transactions_per_month:
            transactions_per_month[expense['month']]['expense'] = expense['total_amount']
        else:
            transactions_per_month[expense['month']] = {'income': 0, 'expense': expense['total_amount']}

    return transactions_per_month

def get_transactions_per_day(user):
    incomes_per_day = Income.objects.filter(user=user).annotate(day=TruncDay('date')).values('day').annotate(
        total_amount=Sum('amount'))
    expenses_per_day = Expense.objects.filter(user=user).annotate(day=TruncDay('date')).values('day').annotate(
        total_amount=Sum('amount'))

    transactions_per_day = {}
    for income in incomes_per_day:
        transactions_per_day[income['day']] = {'income': income['total_amount'], 'expense': 0}

    for expense in expenses_per_day:
        if expense['day'] in transactions_per_day:
            transactions_per_day[expense['day']]['expense'] = expense['total_amount']
        else:
            transactions_per_day[expense['day']] = {'income': 0, 'expense': expense['total_amount']}

    return transactions_per_day

def get_transactions_per_year(user):
    # Получаем сумму доходов и расходов за каждый год
    incomes_per_year = Income.objects.filter(user=user).annotate(year=TruncYear('date')).values('year').annotate(total_amount=Sum('amount'))
    expenses_per_year = Expense.objects.filter(user=user).annotate(year=TruncYear('date')).values('year').annotate(total_amount=Sum('amount'))

    # Создаем словарь, в котором ключами будут годы, а значениями будут суммы доходов и расходов за каждый год
    transactions_per_year = {}
    for income in incomes_per_year:
        transactions_per_year[income['year']] = {'income': income['total_amount'], 'expense': 0}

    for expense in expenses_per_year:
        if expense['year'] in transactions_per_year:
            transactions_per_year[expense['year']]['expense'] = expense['total_amount']
        else:
            transactions_per_year[expense['year']] = {'income': 0, 'expense': expense['total_amount']}

    return transactions_per_year

def get_transactions_history(user):
    # Получаем все транзакции пользователя отсортированные по дням
    incomes = Income.objects.filter(user=user).order_by('date')
    expenses = Expense.objects.filter(user=user).order_by('date')

    # Добавляем метку "Тип" к каждой транзакции
    for income in incomes:
        income.type = 'Доход'
    for expense in expenses:
        expense.type = 'Расход'

    # Слияние доходов и расходов в один список и сортировка по дате
    transactions_history = list(incomes) + list(expenses)
    transactions_history.sort(key=lambda x: x.date)

    return transactions_history
@login_required(login_url='login')
def edit_transaction(request, transaction_id):
    income = get_object_or_404(Income, pk=transaction_id)
    expense = get_object_or_404(Expense, pk=transaction_id)

    if request.method == 'POST':
        if 'income_id' in request.POST:
            form = IncomeForm(request.POST, instance=income)
            if form.is_valid():
                form.save()
                return redirect('profile')
        elif 'expense_id' in request.POST:
            form = ExpenseForm(request.POST, instance=expense)
            if form.is_valid():
                form.save()
                return redirect('profile')
    else:
        if income:
            form = IncomeForm(instance=income)
        else:
            form = ExpenseForm(instance=expense)

    return render(request, 'FinancerApp/edit_transaction.html', {'form': form})

def create_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            return redirect('profile')
    else:
        form = IncomeForm()
    return render(request, 'FinancerApp/create_income.html', {'form': form})

def create_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('profile')
    else:
        form = ExpenseForm()
    return render(request, 'FinancerApp/create_expense.html', {'form': form})


