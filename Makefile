test:
	DJANGO_SETTINGS_MODULE=examples.notepad.notepad.settings \
		python -m django test $${TEST_ARGS:-tests}

admin_build:
	cd siwe_auth/frontend && npm install && npm run build
