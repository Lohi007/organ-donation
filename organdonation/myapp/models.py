from django.db import models

# Create your models here.

class donorregister(models.Model):
    id = models.AutoField(primary_key=True)
    username=models.CharField(max_length=100, null=False)
    age=models.IntegerField(max_length=100, null=False)
    bloodtype=models.CharField(max_length=100, null=False)
    mobno=models.IntegerField(max_length=100, null=False)
    pwd=models.CharField(max_length=100, null=False)
    locn=models.CharField(max_length=300, null=False)
    hname=models.CharField(max_length=300, null=False)
    organavail=models.CharField(max_length=300, null=False)
    chronicdisease=models.CharField(max_length=300, null=False)
    infectious=models.CharField(max_length=200, null=False)
    cancerhistory=models.CharField(max_length=200, null=False)
    medications=models.CharField(max_length=200, null=False)

    def __str__(self):
        return "%s %s %s %s %s %s %s %s %s %s %s %s" %  (
             self.username, self.age, self.bloodtype,self.mobno, self.pwd, self.locn, self.hname,self.organavail,self.chronicdisease,self.infectious,self.cancerhistory,self.medications)


class receiverregister(models.Model):
    id = models.AutoField(primary_key=True)
    rname=models.CharField(max_length=100, null=False)
    rage=models.IntegerField(max_length=100, null=False)
    rbloodtype=models.CharField(max_length=100, null=False)
    rmobno=models.IntegerField(max_length=100, null=False)
    rpwd=models.CharField(max_length=100, null=False)
    rlocn=models.CharField(max_length=300, null=False)
    rhname=models.CharField(max_length=300, null=False)
    organneed=models.CharField(max_length=300, null=False)


    def __str__(self):
        return "%s %s %s %s %s %s %s %s " %  (
             self.rname, self.rage, self.rbloodtype,self.rmobno, self.rpwd, self.rlocn, self.rhname,self.organneed)
