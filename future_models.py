import datetime
import random

from django.db import models
from django.utils import timezone

import sys

# One of the main models are the organizations that are registered to use the site
class Organization(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='companies')
    short_description = models.CharField(max_length=255)
    has_schedule = models.BooleanField(default=False)
    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name
    def getSortedRehearsals(self):
        rehearsals = self.rehearsal_set.all()
        sortedRehearsals = sorted(rehearsals, key = lambda t : len(t.getAvailableCasts()) )
        return sortedRehearsals
    def unscheduleRehearsals(self):
        totalCasts = self.cast_set.all()

        members = Member.objects.filter(company=self)
        for mem in members:
            r = mem.conflict_set.filter(description__startswith="%s Rehearsal" % (self))
            r.delete()

        for cast in totalCasts:
            cast.is_scheduled = False
            cast.rehearsal = None
            cast.save()

        self.has_schedule = False
        self.save()
        return True
        
    def scheduleRehearsals(self):
        totalCasts = self.cast_set.all()
        totalRehearsals = self.rehearsal_set.all()
        # print >> sys.stderr, "Total Casts"
        # print >> sys.stderr, totalCasts

        # print >> sys.stderr, "Total Rehearsals:"
        # print >> sys.stderr, totalRehearsals

        for n in totalCasts:
            minNumCasts = len(totalCasts)

            # find unscheduled rehearsal with least number of available casts (greater than 0)
            for rehearsal in totalRehearsals:
                numCasts = len(rehearsal.getAvailableCasts())
                if numCasts > 0 and numCasts < minNumCasts:
                    minNumCasts = numCasts

            print "Min Number of Casts at Beginning:"
            print minNumCasts

            # add all unscheduled rehearsals with min number to a list
            rehearsal_list = []
            for rehearsal in totalRehearsals:
                if len(rehearsal.getAvailableCasts()) == minNumCasts:
                    rehearsal_list.append(rehearsal)

            print "Rehearsals with min number of casts:"
            print rehearsal_list

            # find unscheduled cast available during rehearsals above with least number of available rehearsals
            minNumRehearsals = len(totalRehearsals)

            for rehearsal in rehearsal_list:
                available_casts = rehearsal.getAvailableCasts()
                for cast in available_casts:
                    numRehearsals = len(cast.getAvailableRehearsals())
                    if numRehearsals < minNumRehearsals:
                        minNumRehearsals = numRehearsals

            print "Min Number of Rehearsals for each cast:"
            print minNumRehearsals


            # add all casts with min number to a list
            cast_list = []
            casts = {}
            for rehearsal in rehearsal_list:
                available_casts = rehearsal.getAvailableCasts()
                for cast in available_casts:
                    if len(cast.getAvailableRehearsals()) == minNumRehearsals:
                        cast_list.append(cast)
                        casts[cast] = rehearsal

            print "Cast-rehearsal pairs where cast has min number of rehearsals:"
            print casts

            if cast_list:
                # randomly pick a cast from the remaining cast_list
                # cast = random.choice(cast_list)
                cast = random.choice(casts.keys())

                print "Randomly chosen cast:"
                print cast
                print casts[cast]

                # schedule the cast to its respective rehearsal
                cast.scheduleRehearsal(casts[cast])
                # rehearsal.is_scheduled = True
                cast.save()
                rehearsal.save()

                print "Is cast scheduled?"
                print cast.is_scheduled

                # print >> sys.stderr, "Is rehearsal scheduled?"
                # print >> sys.stderr, rehearsal.is_scheduled

                #return True

            else:
                self.has_schedule = False
                self.save()
                return "Could not complete scheduling... Too many conflicts"

        self.has_schedule = True
        self.save()
        return "Iteration done"

# Time block model that is extended for conflicts and rehearsals
class TimeBlock(models.Model):
    start_time = models.TimeField('Start Time')
    end_time = models.TimeField('End Time')
    MONDAY = 'MON'
    TUESDAY = 'TUE'
    WEDNESDAY = 'WED'
    THURSDAY = 'THU'
    FRIDAY = 'FRI'
    SATURDAY = 'SAT'
    SUNDAY = 'SUN'
    DAY_OF_WEEK_CHOICES = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    )
    day_of_week = models.CharField(max_length=3, choices=DAY_OF_WEEK_CHOICES, default=MONDAY)
    
    class Meta:
        abstract = True

class Rehearsal(TimeBlock):
    company = models.ForeignKey(Organization)
    place = models.CharField(max_length=200)
    # is_scheduled = models.BooleanField(default=False)
    
    def __str__(self):
        return "%s: %s - %s (%s)" % (self.place, self.start_time, self.end_time, self.day_of_week)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']

    def getAvailableCasts(self):
        casts = Cast.objects.filter(company=self.company)

        cast_list = []
        for cast in casts:
            if cast.is_scheduled == False:
                members = cast.member_set.all()
                for member in members:
                    available = True
                    for conflict in member.conflict_set.all():
                        if conflict.conflictsWith(self):
                            available = False
                            break

                    if available == False:
                        break

                if available == True:
                    cast_list.append(cast)
        return list(cast_list)

class Cast(models.Model):
    company = models.ForeignKey(Organization)
    name = models.CharField(max_length=255)
    rehearsal = models.ForeignKey(Rehearsal, blank=True, null=True)
    is_scheduled = models.BooleanField(default=False)
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def scheduleRehearsal(self, reh):
        self.rehearsal = reh     
        
        # add rehearsal as a conflict for all the cast members
        members = Member.objects.filter(cast=self)
        for mem in members:
            mem.conflict_set.create(description="%s Rehearsal (%s)" % (self.company, self.name), start_time=reh.start_time, end_time=reh.end_time, day_of_week=reh.day_of_week)

        self.is_scheduled = True
        # reh.is_scheduled = True

    def getAvailableRehearsals(self):
        rehearsals = self.company.rehearsal_set.all()
        members = self.member_set.all()

        rehearsal_list = []
        for rehearsal in rehearsals:
            available = True
            for member in members:
                for conflict in member.conflict_set.all():
                    if conflict.description != 'Rehearsal':
                        if conflict.conflictsWith(rehearsal):
                            available = False
                            break
                if available == False:
                    break

            if available == True:
                rehearsal_list.append(rehearsal)
        return list(rehearsal_list)

# Everybody is characterized as a person... Each person is organized under either student or non-student
class Person(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(max_length=254)
    organization = models.ManyToManyField(Organization)
    cast = models.ManyToManyField(Cast, blank=True)

    class Meta:
        ordering = ['email', 'first_name']

class Student(Person):
    netid = models.CharField(max_length=100)
    def __str__(self):
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        return self.netid

class nonStudent(Person):
    password = models.PasswordField(max_length=200)
    def __str__(self):
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        return self.email

# People can also be admins of whatever organization their a part of
class Admin(models.Model):
    member = models.ForeignKey(Person)
    organization = models.ForeignKey(Organization)
    def __str__(self):
        return self.member

    class Meta:
        ordering = ['member']
    
class Choreographer(models.Model):
    member = models.ForeignKey(Person)
    organization = models.ForeignKey(Organization)
    cast = models.ForeignKey(Cast)

    def __str__(self):
        return self.member
        
    class Meta:
        ordering = ['member']
