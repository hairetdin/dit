from django.db import models
from datetime import datetime
from django.utils import timezone
from django.db.models import signals
from django.contrib.auth.models import User
from contact.models import Employee


class Mission(models.Model):
    date_created = models.DateTimeField('Дата создания', blank=True, null=True)
    initiator = models.ForeignKey(Employee, related_name="initiator", blank=True, null=True, verbose_name = "Инициатор")
    creator = models.ForeignKey(User, related_name="mission_creator", blank=True, null=True, verbose_name = "Кто создал")
    customer = models.ForeignKey(Employee, verbose_name = "Заказчик")
    subject = models.TextField('Текст задания')
    date_exec_max = models.DateTimeField('Крайний срок', blank=True, null=True)
    date_closed = models.DateTimeField('Дата закрытия', blank=True, null=True)

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        
    def __str__(self):
        return '%s %s' % (self.date_created, self.subject)

    def save(self, *args, **kwargs):
        if not self.date_created:
            #self.date_created = datetime.now()
            self.date_created = timezone.now()
        super(Mission, self).save(*args, **kwargs)


class Comment(models.Model):
    creator = models.ForeignKey(User, related_name="comment_creator", blank=True, null=True)
    mission = models.ForeignKey(Mission)
    text = models.TextField()
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        
    def __str__(self):
        return '%s %s' % (self.mission, self.text)



class Executor(models.Model):
    employee = models.ForeignKey(Employee, verbose_name = "Работник")

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'
        
    def __str__(self):
        return '%s' % (self.employee)

def execmiss_closed(sender, instance, created, **kwargs):
    mission_closed = []
    for executor in instance.mission.executormission_set.all():
        mission_closed.append(executor.date_closed)
    if None in mission_closed:
        instance.mission.date_closed = None
        instance.mission.save()
    else:
        instance.mission.date_closed = max(mission_closed)
        instance.mission.save()

class ExecutorMission(models.Model):
    mission = models.ForeignKey(Mission)
    executor = models.ForeignKey(Executor, verbose_name = "Исполнитель")
    date_accepted = models.DateTimeField('Принято к исполнению', blank=True, null=True)
    date_closed = models.DateTimeField('Выполнено', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'
        
    def __str__(self):
        return '%s' % (self.mission)
    #    return '%s %s %s %s' % (self.mission, self.executor, self.date_accepted, self.date_closed)
signals.post_save.connect(execmiss_closed, sender=ExecutorMission)
