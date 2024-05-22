from django.shortcuts import render, redirect
from .models import LeaveRequest, Task
import datetime
from .responses import responses
import random

def form(request):
    return render(request, 'chatbot.html')

def view_leave_request(request):
    leave_requests = LeaveRequest.objects.all()
    context = {'leave_requests': leave_requests,'date':leave_requests}
    return render(request, 'chatbot.html', context)

def view_tasks(request):
    task = Task.objects.all()
    context = {'tasks': task}
    return render(request, 'chatbot.html', context)

def chatbot(request):
    context = {}

    # Initialize chat log in session if not present
    if 'chat_log' not in request.session:
        request.session['chat_log'] = []

    # Initialize alert_displayed in session if not present
    if 'alert_displayed' not in request.session:
        request.session['alert_displayed'] = False

    # ALERT: Check for tasks due tomorrow if alert has not been displayed yet
    if not request.session['alert_displayed']:
        current_datetime = datetime.date.today()
        next_day = current_datetime + datetime.timedelta(days=1)
        ob = Task.objects.filter(deadline=next_day)
        if ob.exists():
            task_names_due_tomorrow = ", ".join(i.task_name for i in ob)
            alert_msg = f'{task_names_due_tomorrow} is pending tomorrow'
            request.session['chat_log'].append({'response': alert_msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
            request.session['alert_displayed'] = True
            request.session.modified = True

    if request.method == "POST":
        user_input = request.POST.get('user_input', '')
        request.session['chat_log'].append({'user': user_input, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

        if user_input.strip().lower() == 'view leaves':
            leave_requests = LeaveRequest.objects.all()
            leave_msgs = [f'Leave Request: {lr.reason} {lr.leave_date}' for lr in leave_requests]
            
            request.session['chat_log'].extend([{'response': msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} for msg in leave_msgs])

        elif 'request leave' in user_input:
            global dte
            #format for leave : request leave for 01/01/2022 with reason fever
            words = user_input.split()
            try:

                reason_index = words.index("reason")
                date_index = words.index("leave")
                dte = words[date_index + 2]
                reason = "".join(words[reason_index + 1])
                dtea = datetime.datetime.strptime(dte, "%d/%m/%Y")
                LeaveRequest(reason=reason,leave_date=dtea).save()
                response_msg = f'Leave requested with reason: {reason} on {dtea}.'
            except ValueError:
                response_msg = 'Invalid Message'
            request.session['chat_log'].append({'response': response_msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

        elif 'deadline' in user_input:
            #format for task : design the webpage deadline 01/01/2022
            words = user_input.split()
            d_index = words.index("deadline")
            task = " ".join(words[:d_index])
            date_str = words[d_index + 1]
            try:
                date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                Task(task_name=task, deadline=date).save()
                response_msg = f'Task "{task}" scheduled for completion on {date}.'
            except ValueError:
                response_msg = 'Invalid date format. Please use the format DD/MM/YYYY.'
            request.session['chat_log'].append({'response': response_msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

        elif 'view tasks' in user_input:
            tasks = Task.objects.all()
            task_msgs = [f'Task: {task.task_name}' for task in tasks]
            request.session['chat_log'].extend([{'response': msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")} for msg in task_msgs])
        
        elif user_input in responses:
            response_msg = f'{random.choice(responses[user_input])}.'
            request.session['chat_log'].append({'response': response_msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

        elif 'task' in user_input and 'completed' in user_input and 'date' in user_input:
            # format : completed task design the webpage on date 28/06/2024
            words = user_input.split()
            t_index = words.index("task")
            dt_index = words.index("date")
            tsk = " ".join(words[t_index+1:dt_index-1])
            dat_str = words[dt_index+1]
            try:
                dat = datetime.datetime.strptime(dat_str, "%d/%m/%Y").date()
                task_obj = Task.objects.get(task_name=tsk, deadline=dat)
                task_obj.delete()
                response_msg = f'{tsk} was successfully completed on {dat}'
            except Task.DoesNotExist:
                response_msg = 'No task found with the given name and date'
            except ValueError:
                response_msg = 'Invalid date format. Please use DD/MM/YYYY.'
            request.session['chat_log'].append({'response': response_msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
        
        
        #below are condition for inavlid commands to handle errors
        

        else:
            response_msg = f'{user_input} is not a valid command'
            request.session['chat_log'].append({'response': response_msg, 'timestamp': datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")})

        request.session.modified = True

    context['chat_log'] = request.session['chat_log']
    return render(request, 'chatbot.html', context)