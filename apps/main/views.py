from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime, date, time
from .models import *
import bcrypt
# Create your views here.
def index(request):
	return render(request, 'main/index.html')

def store(request):
	user = User.objects.filter(id=request.session['user_id']).first()
	players = Player.objects.all()
	current_player = user.players.first()
	context = {
		"curr_user": User.objects.get(id=request.session['user_id']),
		"current_player": current_player,
	}
	return render(request, 'main/store.html', context)

def create_user(request):
	if User.objects.validate(request,request.POST) == True:
		user = User.objects.create(
			name = request.POST.get('name'),
			alias = request.POST.get('alias'),
			email = request.POST.get('email'),
			password = bcrypt.hashpw(request.POST.get('password').encode(), bcrypt.gensalt())
		)
		request.session['user_id'] = user.id
		return redirect('/create_page')
	return redirect('/')

def login_user(request):
	login = User.objects.login_user(request,request.POST)
	if login[0]:
		request.session['user_id'] = login[1].id
		return redirect('/home')
	return redirect('/')

def logout(request):
	del request.session['user_id']
	return redirect('/')

def create_page(request):
	context = {
		'users': User.objects.all(),
		'curr_user': User.objects.get(id=request.session['user_id'])
	}
	return render(request, 'main/create_player.html', context)

def home(request):
	now = datetime.now().strftime('%M')
	increment = Increment.objects.first()
	values = [1,2,3,4,5,6,7,8,9,10]
	for i in values:
		if int(now) == i and increment.state == 'False':
			messages.add_message(request, messages.INFO, "Everybody got $100!")
			increment.state = 'True'
			increment.save()
			everyone = Player.objects.all()
			for person in everyone:
				person.money += 100
				person.save()
		elif int(now) != i:
			increment.state = 'False'
			increment.save()

	user = User.objects.filter(id=request.session['user_id']).first()
	players = Player.objects.all()
	current_player = user.players.first()

	players_dead = Grave.objects.all()
	grave_ids = []
	for grave in players_dead:
		grave_ids.append(grave.id)
	players_alive = Player.objects.exclude(graves__id__in=grave_ids)

	context = {
		"curr_user": User.objects.get(id=request.session['user_id']),
		"players": players_alive,
		"deads": players_dead,
		"current_player": current_player,
	}
	return render(request, 'main/home.html', context)


def create_player(request, user_id):
	if 'class_type' not in request.POST:
		messages.add_message(request, messages.INFO, "Please select a class!")
		return redirect('/create_page')
	else:
		user = User.objects.get(id=user_id)
		if request.POST['class_type'] == 'Mafia':
			Player.objects.create(
				class_type = request.POST['class_type'],
				money = 150,
				attack = 5,
				medicine = 1,
				coffee = 0,
				user=user
			)
		if request.POST['class_type'] == 'Security':
			Player.objects.create(
				class_type = request.POST['class_type'],
				health = 4,
				attack = 4,
				medicine = 2,
				coffee = 0,
				user=user
			)
		if request.POST['class_type'] == 'Programmer':
			Player.objects.create(
				class_type = request.POST['class_type'],
				health = 2,
				money = 100,
				attack = 2,
				medicine = 1,
				coffee = 1,
				user=user
			)
		return redirect('/home')


def attack(request, player_id):
	user = User.objects.get(id=request.session['user_id'])
	player = Player.objects.get(id=player_id)
	attacker = Player.objects.get(user__id=user.id)
	if player.health > 0:
		player.health -= 1
		attacker.attack -= 1
		attacker.save()
		player.save()
		return redirect('/home')
	else:
		player.status = "Knocked Out"
		attacker.money += 50
		attacker.attack -= 1
		attacker.save()
		player.save()
		Grave.objects.create(
			player=player,
			user=player.user
		)
		return redirect('/home')

def use_item(request, player_id, item_type):
	player = Player.objects.get(id=player_id) ##Using current_player instead of something else
	if item_type == "medicine" and player.health > 0:
		if player.health > 6:
			messages.add_message(request, messages.INFO, "Eh, you're healthy enough already.")
		elif player.health == 0:
			messages.add_message(request, messages.INFO, "You're asleep. A medkit ain't gonna do nothing.")
		elif player.medicine > 0:
			player.medicine -= 1
			player.health += 2
			player.save()
		elif player.medicine == 0:
			messages.add_message(request, messages.INFO, "You don't have any Medicine! This isn't free healthcare!")
	if item_type == "coffee":
		if player.coffee > 0 and player.health == 0:
			player.coffee -= 1
			player.health += 3
			player.save()
		elif player.coffee == 0:
			messages.add_message(request, messages.INFO, "You don't have any Coffee! Go to the Starbucks or something.")
		elif player.health > 0:
			messages.add_message(request, messages.INFO, "I don't think you should be drinking any coffee.")
	return redirect('/home')

def buy_item(request, player_id, item_type):
	player = Player.objects.get(id=player_id) ##Using current_player instead of something else
	if item_type == "attack" and player.money >= 25:
		messages.add_message(request, messages.INFO, "Thanks for buying an Attack Token!")
		player.attack += 1
		player.money -= 25
		player.save()
	elif item_type == "attack" and player.money < 25:
		messages.add_message(request, messages.INFO, "You don't have enough money to buy an Attack Token! Get out!")

	if item_type == "medicine" and player.money >= 50:
		messages.add_message(request, messages.INFO, "Thanks for buying a Medicine!")
		player.medicine += 1
		player.money -= 50
		player.save()
	elif item_type == "medicine" and player.money < 50:
		messages.add_message(request, messages.INFO, "You don't have enough money to buy Medicine! We don't provide free healthcare!")

	if item_type == "coffee" and player.money >= 100:
		messages.add_message(request, messages.INFO, "Thanks for buying a Coffee!")
		player.coffee += 1
		player.money -= 100
		player.save()
	elif item_type == "coffee" and player.money < 100:
		messages.add_message(request, messages.INFO, "You don't have enough money to buy a Coffee! Looks like you're gonna stay asleep...")
	return redirect('/store')

def revive(request, grave_id):
	print grave_id
	grave = Grave.objects.get(id=grave_id)
	player_id = grave.player.id
	grave.delete()
	player = Player.objects.get(id=player_id)
	player.health += 2
	player.status = "Alive"
	player.save()
	return redirect('/home')
