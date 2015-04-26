from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from companies.models import Company, Member, Admin, Rehearsal, Cast, MemberForm
from profiles.models import ConflictForm, RehearsalForm, CreateCastForm

from profiles.functions import memberAuth, profileAuth, adminAuth

# Create your views here.
def profile(request, company_name, member_name):
    # check if valid member
    not_valid_member = memberAuth(request, company_name, member_name)
    if not_valid_member:
        return not_valid_member
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(netid=member_name)
        if member.first_name and member.last_name:
            try:
                admin = Admin.objects.get(member=member)
            except (KeyError, Admin.DoesNotExist):
                return render(request, 'profiles/dancer.html', {'member':member, 'company':company})
            else:
                return render(request, 'profiles/admin.html', {'member':member, 'company':company})
        # if you need to enter your information ...
        else:
            # process the form and conflict data of the user
            if request.method == 'POST':
                form = MemberForm(request.POST, instance=member)
                if form.is_valid():
                    form.save()

                    return redirect('profiles:profile', company_name, member_name,)
            else:
                form = MemberForm(instance=member)
            return render(request, 'profiles/name.html', {'company':company, 'member':member, 'form':form})

def conflicts(request, company_name, member_name):
    # check if came from profile
    not_from_profile = profileAuth(request, company_name, member_name)
    if not_from_profile:
        return not_from_profile
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(netid=member_name)    

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
        return render(request, 'profiles/addconflict.html', {'company':company, 'member':member, 'conflict_list':conflict_list, 'form':form})
    

def spaces(request, company_name, member_name):
    # check if valid admin
    not_valid_admin = adminAuth(request, company_name, member_name)
    if not_valid_admin:
        return not_valid_admin
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(netid=member_name)

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
        return render(request, 'profiles/addspace.html', {'company':company, 'member':member, 'rehearsal_list':rehearsal_list, 'form':form})
    

def members(request, company_name, member_name):
    # check if valid admin
    not_valid_admin = adminAuth(request, company_name, member_name)
    if not_valid_admin:
        return not_valid_admin
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(netid=member_name)
        
        member_list = company.member_set.all()
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

def casts(request, company_name, member_name):
    # check if valid admin
    not_valid_admin = adminAuth(request, company_name, member_name)
    if not_valid_admin:
        return not_valid_admin
    else:
        company = Company.objects.get(name=company_name)
        member = company.member_set.get(netid=member_name)

        member_list = company.member_set.all()
        total_casts = Cast.objects.all()

        # process the form and conflict data of the user
        if request.method == 'POST':
            form = CreateCastForm(request.POST)
            if form.is_valid():
                new_cast = form.save(commit=False)
                new_cast.company = company
                new_cast.save()
                form.save_m2m()

                return HttpResponseRedirect('')
        else:
            form = CreateCastForm()
        return render(request, 'profiles/casts.html', {'company':company, 'member':member, 'member_list':member_list, 'total_casts':total_casts, 'form':form})
