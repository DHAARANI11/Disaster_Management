run: run-android run-ios

run-android:
	cd app && npx react-native start

run-ios:
	cd app && npm run ios -- --simulator='iPhone 14 Pro Max'

server:
	\envs\Dis\Scripts\activate && cd api && python manage.py runserver

redis:
	redis-server