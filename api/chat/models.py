from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser


def upload_thumbnail(instance, filename):
	path = f'thumbnails/{instance.username}'
	extension = filename.split('.')[-1]
	if extension:
		path = path + '.' + extension
	return path

class User(AbstractUser):

	MALE = 'M'
	FEMALE='F'
	OTHER = 'O'

    
	GENDER_CHOICES=[
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]

    
	ORGANIZATION_TYPES = [
		('medical','Medical'),
        ('tsunami', 'Tsunami'),
        ('flood', 'Flood'),
        ('cyclone', 'Cyclone'),
        ('Earth Quake', 'Earth Quake'),
        ('storm', 'Storm'),
		('other','Other')
    ]

    
	DISTRICT_CHOICES = [
        ('ariyalur', 'Ariyalur'),
        ('chennai', 'Chennai'),
        ('coimbatore', 'Coimbatore'),
        ('cuddalore', 'Cuddalore'),
        ('dharmapuri', 'Dharmapuri'),
        ('dindigul', 'Dindigul'),
        ('erode', 'Erode'),
        ('kanchipuram', 'Kanchipuram'),
        ('kanyakumari', 'Kanyakumari'),
        ('karur', 'Karur'),
        ('krishnagiri', 'Krishnagiri'),
        ('madurai', 'Madurai'),
        ('nagapattinam', 'Nagapattinam'),
        ('namakkal', 'Namakkal'),
        ('perambalur', 'Perambalur'),
        ('pudukkottai', 'Pudukkottai'),
        ('ramanathapuram', 'Ramanathapuram'),
        ('salem', 'Salem'),
        ('sivagangai', 'Sivagangai'),
        ('thanjavur', 'Thanjavur'),
        ('theni', 'Theni'),
        ('thiruvallur', 'Thiruvallur'),
        ('thiruvarur', 'Thiruvarur'),
        ('thoothukudi', 'Thoothukudi'),
        ('tiruchirappalli', 'Tiruchirappalli'),
        ('tirunelveli', 'Tirunelveli'),
        ('tiruppur', 'Tiruppur'),
        ('trichy', 'Trichy'),
        ('tuticorin', 'Tuticorin'),
        ('vellore', 'Vellore'),
        ('villupuram', 'Villupuram'),
        ('virudhunagar', 'Virudhunagar'),
    ]



    
	username = models.CharField(max_length=30, unique=True,null=True)
    
	first_name = models.CharField(max_length=30, null=True)
    
	last_name = models.CharField(max_length=30,null=True)
    
	password = models.CharField(max_length=128,null=True)  
    
	password2 = models.CharField(max_length=128,null=True)
    
	email = models.EmailField(max_length=40,unique=True)  
    
	phone_no = models.CharField(max_length=10, blank=True, null=True)
    
	adhaar_no = models.CharField(max_length=12, unique=True, blank=True, null=True)
    
	address = models.TextField(blank=True, null=True)
    
	pincode = models.CharField(max_length=6, blank=True, null=True)
    
	organization_name = models.CharField(max_length=255, blank=True, null=True)
    
	profession = models.CharField(max_length=100,blank=True, null=True)
    
	organization_address = models.TextField(blank=True, null=True)
     
	lattitude = models.DecimalField(max_digits=10,decimal_places=4, blank=True, null=True)
    
	longitude = models.DecimalField(max_digits=10,decimal_places=4, blank=True, null=True)
    
	location = models.CharField(max_length=100,choices=DISTRICT_CHOICES,blank=True, null=True)
    
	Org_pincode = models.CharField(max_length=6, blank=True, null=True)
    
	thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)





    
	def get_full_name(self):
        
		return f"{self.first_name} {self.last_name}".strip()

    
	def __str__(self):
        
		return self.get_full_name()


class Team(models.Model):
    username = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    disaster_type = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

class Connection(models.Model):
	sender = models.ForeignKey(
		User,
		related_name='sent_connections',
		on_delete=models.CASCADE
	)
	receiver = models.ForeignKey(
		User,
		related_name='received_connections',
		on_delete=models.CASCADE
	)
	accepted = models.BooleanField(default=False)
	updated = models.DateTimeField(auto_now=True)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.sender.username + ' -> ' + self.receiver.username



class Message(models.Model):
	connection = models.ForeignKey(
		Connection,
		related_name='messages',
		on_delete=models.CASCADE
	)
	user = models.ForeignKey(
		User,
		related_name='my_messages',
		on_delete=models.CASCADE
	)
	text = models.TextField()
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.user.username + ': ' + self.text


class Room(models.Model):
    WAITING = 'waiting'
    ACTIVE = 'active'
    CLOSED = 'closed'

    CHOICES_STATUS = (
        (WAITING, 'Waiting'),
        (ACTIVE, 'Active'),
        (CLOSED, 'Closed'),
    )

    uuid = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    agent = models.ForeignKey(User, related_name='rooms', blank=True, null=True, on_delete=models.SET_NULL)
    messages = models.ManyToManyField(Message, blank=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=CHOICES_STATUS, default=WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return f'{self.client} - {self.uuid}'
