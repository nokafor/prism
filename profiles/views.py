from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from companies.models import Company, Member, Admin, Rehearsal, Cast, Choreographer, TimeBlock
from updates.forms import ConflictForm, RehearsalForm, CastForm, MemberForm, MemberNameForm, AdminForm, ChoreographerForm

from profiles.functions import memberAuth, adminAuth
from django.contrib.auth.models import User, Group

from datetime import datetime
from django.utils import timezone

# Create your views here.
def testing(request, company_name, member_name):
    # make sure member is logged in and has access to this page
    member = memberAuth(request, company_name, member_name)

    if member:
        # make sure member is an admin and has the right to access this information
        admin = adminAuth(request, company_name, member_name)

        if admin:
            if request.method == 'POST':
                try: 
                    valid_datetime = datetime.strptime(request.POST['datetimepicker4'], '%m/%d/%Y %I:%M %p')
                    print valid_datetime
                    company = Company.objects.get(name=company_name)
                    company.conflicts_due = valid_datetime.replace(tzinfo=timezone.now().tzinfo)
                    company.save()
                    return redirect('profiles:profile', company_name=company_name, member_name=member_name)
                except ValueError:
                    return HttpResponse('You did not enter a valid date and time. So the information was not saved.')

            return render(request, 'profiles/test.html', {'company_name':company_name, 'member_name':member_name})

    # admins and members logged in under the wrong name cannot access this page
    return HttpResponse('Hello____, You do not have access to this page. Please log into the appropriate company, or sign out here.')

    

def profile(request, company_name, member_name):
    # make sure member has access to this profile
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)

        # process the form and conflict data of the user
        if request.method == 'POST':
            form = MemberNameForm(request.POST, instance=member)
            if form.is_valid():
                form.save()

                return redirect('profiles:profile', company_name, member_name,)
        else:
            form = MemberNameForm(instance=member)

        return render(request, 'profiles/hub.html', {'member':member, 'company':company, 'form':form})

    else:
        return HttpResponse('Hello____, You do not have access to this page. Please log into the appropriate company, or sign out here.')

def members(request, company_name, member_name):
    # make sure member has access to this profile
    member = memberAuth(request, company_name, member_name)

    if member:
        company = Company.objects.get(name=company_name)
        member_list = User.objects.filter(groups__name=company_name)
        admin_list = company.admin_set.all()

        # process the form and conflict data of the user
        if request.method == 'POST':
            member_form = MemberForm(request.POST)
            if member_form.is_valid():
                new_member = member_form.save(commit=False)
                new_member.company = company
                new_member.save()
                member_form.save_m2m()

                return HttpResponseRedirect('')
        else:
            member_form = MemberForm()
        return render(request, 'profiles/members.html', {'company':company, 'member':member, 'member_list':member_list, 'admin_list':admin_list, 'member_form':member_form})

    else:
        return HttpResponse('Hello____, You do not have access to this page. Please log into the appropriate company, or sign out here.')

def conflicts(request, company_name, member_name):
    # check if came from profile
    not_from_profile = profileAuth(request, company_name, member_name)
    if not_from_profile:
        return not_from_profile
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(username=member_name)    

        conflict_list = member.conflict_set.all()

        # process the form and conflict data of the user
        if request.method == 'POST':
            form = ConflictForm(request.POST)
            if form.is_valid():
                new_conflict = form.save(commit=False)
                new_conflict.member = member
                new_conflict.save()
                form.save_m2m()

                return HttpResponseRedirect('')
        else:
            form = ConflictForm()
        return render(request, 'profiles/addconflict.html', {'company':company, 'member':member, 'conflicts':conflict_list, 'form':form, 'timeblock':TimeBlock})
    

def spaces(request, company_name, member_name):
    # check if valid admin
    not_valid_admin = adminAuth(request, company_name, member_name)
    if not_valid_admin:
        return not_valid_admin
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(username=member_name)

        rehearsal_list = company.rehearsal_set.all()

        # process the form and conflict data of the user
        if request.method == 'POST':
            form = RehearsalForm(request.POST)
            if form.is_valid():
                new_rehearsal = form.save(commit=False)
                new_rehearsal.company = company
                new_rehearsal.save()
                form.save_m2m()

                return HttpResponseRedirect('')
        else:
            form = RehearsalForm()
        return render(request, 'profiles/addspace.html', {'company':company, 'member':member, 'rehearsals':rehearsal_list, 'form':form, 'timeblock':TimeBlock})


def casts(request, company_name, member_name):
    # check if valid admin
    not_valid_admin = adminAuth(request, company_name, member_name)

    company = Company.objects.get(name=company_name)
    member = company.member_set.get(username=member_name)

    total_casts = Cast.objects.filter(company=company)
    total_choreographers = Choreographer.objects.filter(company=company)

    if not_valid_admin:
        not_valid_member = memberAuth(request, company_name, member_name)
        if not_valid_member:
            return not_valid_member
        else:
            return render(request, 'profiles/viewcasts.html', {'company':company, 'member':member, 'total_casts':total_casts, 'total_choreographers':total_choreographers})
    else:
        return render(request, 'profiles/casts.html', {'company':company, 'member':member, 'total_casts':total_casts, 'total_choreographers':total_choreographers})

def scheduling(request, company_name, member_name):
    # check if valid admin
    not_valid_admin = adminAuth(request, company_name, member_name)
    if not_valid_admin:
        return not_valid_admin
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(username=member_name)
        rehearsals = company.getSortedRehearsals()

        casts = Cast.objects.filter(company=company)

        return render(request, 'profiles/schedule.html', {'company':company, 'member':member, 'cast_list':casts, 'rehearsal_list':rehearsals})
